import os
import sys
import json
import time
import uuid
import requests
from dotenv import dotenv_values
from playwright.sync_api import sync_playwright

env_staging = dotenv_values(".env.staging")
SUPABASE_URL = env_staging.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_ANON_KEY = env_staging.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = env_staging.get("SUPABASE_SERVICE_ROLE_KEY")
BACKEND_URL = env_staging.get("BACKEND_URL", "https://knowflow-ai-4ssd.onrender.com").rstrip("/")
FRONTEND_URL = env_staging.get("FRONTEND_URL", "https://knowflow-ai-pied.vercel.app").rstrip("/")

print("=== STARTING CLOUD AUTH & RATE LIMIT VERIFICATION ===")
print(f"Frontend: {FRONTEND_URL}")
print(f"Backend: {BACKEND_URL}")
print(f"Supabase: {SUPABASE_URL}")

headers_admin_sb = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
}

# ----------------------------------------------------
# 1. REAL EMAIL CONFIRMATION & SESSION LIFECYCLE
# ----------------------------------------------------
test_id = uuid.uuid4().hex[:6]
test_email = f"e2e_verify_{test_id}@knowflow.test"
test_password = "E2E_SecurePassword123!"

print(f"\n[Step 1] Registering user: {test_email}")
# 1. Create signup link via Supabase GoTrue
gen_res = requests.post(
    f"{SUPABASE_URL}/auth/v1/admin/generate_link",
    headers=headers_admin_sb,
    json={
        "type": "signup",
        "email": test_email,
        "password": test_password,
        "options": {
            "redirectTo": f"{FRONTEND_URL}/auth/callback"
        }
    },
    timeout=15
)
gen_data = gen_res.json()
action_link = gen_data.get("action_link")
user_id = gen_data.get("id")
print(f"  * Generated action link: {action_link[:80]}...")

auth_flow_success = False
landed_url = ""
session_persisted = False
localhost_leaks = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    def handle_req(req):
        if "localhost" in req.url or "127.0.0.1" in req.url:
            localhost_leaks.append(req.url)

    page.on("request", handle_req)

    print("  * Navigating Playwright directly to confirmation link...")
    page.goto(action_link, wait_until="networkidle")
    page.wait_for_timeout(4000)
    landed_url = page.url
    print(f"  * Landed URL after confirmation: {landed_url}")

    # Verify session in localStorage / cookies
    cookies = context.cookies()
    has_sb_token = any("sb-" in c["name"] or "token" in c["name"] or "auth" in c["name"] for c in cookies)
    print(f"  * Auth cookie present: {has_sb_token}")

    # Check reload persistence
    print("  * Reloading page to verify session persistence...")
    page.reload(wait_until="networkidle")
    page.wait_for_timeout(2000)
    after_reload_url = page.url
    print(f"  * URL after reload: {after_reload_url}")
    session_persisted = ("/login" not in after_reload_url)

    # Logout
    print("  * Testing sign out...")
    sign_out_btn = page.query_selector("button:has-text('Sign out'), button:has-text('Logout')")
    if sign_out_btn:
        sign_out_btn.click()
        page.wait_for_timeout(2000)
        print(f"  * URL after sign out: {page.url}")

    browser.close()

auth_flow_success = (len(localhost_leaks) == 0) and ("localhost" not in landed_url) and session_persisted
print(f"==> Auth Confirmation Verdict: {'PASS' if auth_flow_success else 'FAIL'}")

# ----------------------------------------------------
# 2. REAL PASSWORD RECOVERY FLOW
# ----------------------------------------------------
print(f"\n[Step 2] Testing Password Recovery for: {test_email}")
rec_res = requests.post(
    f"{SUPABASE_URL}/auth/v1/admin/generate_link",
    headers=headers_admin_sb,
    json={
        "type": "recovery",
        "email": test_email,
        "options": {
            "redirectTo": f"{FRONTEND_URL}/update-password"
        }
    },
    timeout=15
)
rec_data = rec_res.json()
recovery_link = rec_data.get("action_link")
print(f"  * Generated recovery link: {recovery_link[:80]}...")

new_password = "NewE2E_SecurePassword456!"
recovery_flow_success = False

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    print("  * Navigating to recovery link...")
    page.goto(recovery_link, wait_until="networkidle")
    page.wait_for_timeout(3000)
    print(f"  * Landed URL on recovery: {page.url}")

    # Fill new password and confirm password
    pwd_input = page.query_selector("input#password, input[name='password']")
    confirm_pwd_input = page.query_selector("input#confirm-password, input[name='confirm-password']")
    if pwd_input and confirm_pwd_input:
        pwd_input.fill(new_password)
        confirm_pwd_input.fill(new_password)
        submit_btn = page.query_selector("button[type='submit']")
        if submit_btn:
            submit_btn.click()
            page.wait_for_timeout(4000)
            print(f"  * Submitted new password. Current URL: {page.url}")
            recovery_flow_success = True

    browser.close()

# Verify login with new password via API
login_verify = requests.post(
    f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
    headers={"apikey": SUPABASE_ANON_KEY},
    json={"email": test_email, "password": new_password},
    timeout=15
)
new_pwd_valid = login_verify.status_code == 200
print(f"  * Verification of new password login: {login_verify.status_code} (Valid: {new_pwd_valid})")
print(f"==> Password Recovery Verdict: {'PASS' if new_pwd_valid else 'FAIL'}")

# ----------------------------------------------------
# 3. CONTROLLED RATE LIMITING TEST
# ----------------------------------------------------
print(f"\n[Step 3] Testing Rate Limiting on Live Cloud Backend...")
status_sequence = []
retry_after_header = None
rate_limit_activated = False
activation_index = -1

# Get valid token for search rate limiting
auth_token = login_verify.json().get("access_token", "") if new_pwd_valid else ""
auth_headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}

print(f"  * Sending controlled burst of 75 requests to /api/v1/search (Limit: 60 req/min)...")
for i in range(1, 76):
    try:
        r = requests.get(f"{BACKEND_URL}/api/v1/search?query=healthcheck_rate_limit", headers=auth_headers, timeout=10)
        status_sequence.append(r.status_code)
        if r.status_code == 429:
            rate_limit_activated = True
            activation_index = i
            retry_after_header = r.headers.get("Retry-After")
            print(f"  * Rate limit activated at request #{i} with status 429! Retry-After: {retry_after_header}s, Body: {r.text[:100]}")
            break
    except Exception as e:
        status_sequence.append(f"ERR: {e}")
        break

print(f"  * Request count sent: {len(status_sequence)}")
print(f"  * Status sequence sample: {status_sequence[:10]} ... {status_sequence[-5:]}")
print(f"==> Rate Limiting Enforcement Verdict: {'PASS' if rate_limit_activated else 'FAIL / NOT IMPLEMENTED'}")

# Clean up test user
if user_id:
    requests.delete(f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}", headers=headers_admin_sb)
    print(f"\n[Cleanup] Deleted test user {user_id}")

print("\n=== CLOUD VERIFICATION FINISHED ===")
