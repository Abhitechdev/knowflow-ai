import os
import sys
import time
import uuid
import requests
from dotenv import dotenv_values
from playwright.sync_api import sync_playwright

env_staging = dotenv_values(".env.staging")
SUPABASE_URL = env_staging.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_ANON_KEY = env_staging.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = env_staging.get("SUPABASE_SERVICE_ROLE_KEY")
FRONTEND_URL = env_staging.get("FRONTEND_URL", "https://knowflow-ai-pied.vercel.app").rstrip("/")

print("=== BLOCKER 2: TESTING LIVE VERCEL PASSWORD RECOVERY LIFECYCLE ===")

headers_admin = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
}

test_id = uuid.uuid4().hex[:6]
test_email = f"recovery_e2e_{test_id}@testflow.io"
orig_password = "InitialPassword123!"
new_password = "NewUpdatedPassword2026!"

# 1. Create confirmed user
u_res = requests.post(
    f"{SUPABASE_URL}/auth/v1/admin/users",
    headers=headers_admin,
    json={"email": test_email, "password": orig_password, "email_confirm": True},
    timeout=15
)
user_id = u_res.json().get("id")
print(f"1. Created test user: {test_email} (ID: {user_id})")

# 2. Generate recovery link
rec_res = requests.post(
    f"{SUPABASE_URL}/auth/v1/admin/generate_link",
    headers=headers_admin,
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
print(f"2. Generated recovery link: {recovery_link[:80]}...")

# 3. Navigate recovery link in Playwright browser
localhost_leaks = []
final_page_url = ""
form_submitted = False

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    def handle_req(req):
        if "localhost" in req.url or "127.0.0.1" in req.url:
            localhost_leaks.append(req.url)

    page.on("request", handle_req)

    print("3. Navigating to recovery link...")
    page.goto(recovery_link, wait_until="networkidle")
    page.wait_for_timeout(3000)
    print(f"   Landed on: {page.url}")

    # If redirected or landed on root with hash, check if update-password form appears
    if "/update-password" not in page.url:
        print(f"   Navigating directly to /update-password with session...")
        page.goto(f"{FRONTEND_URL}/update-password", wait_until="networkidle")
        page.wait_for_timeout(2000)

    # Fill new password and confirm password
    pwd_input = page.query_selector("input#password, input[name='password']")
    confirm_pwd_input = page.query_selector("input#confirm-password, input[name='confirm-password']")
    submit_btn = page.query_selector("button[type='submit']")

    if pwd_input and confirm_pwd_input and submit_btn:
        print("4. Filling new password into /update-password form...")
        pwd_input.fill(new_password)
        confirm_pwd_input.fill(new_password)
        submit_btn.click()
        page.wait_for_timeout(4000)
        form_submitted = True
        print(f"   Form submitted! URL after submit: {page.url}")
    else:
        print("   >>> Could not locate password form fields!")

    final_page_url = page.url
    browser.close()

# 4. Verify login with NEW password
print("\n5. Verifying login with NEW password against Supabase GoTrue...")
login_new = requests.post(
    f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
    headers={"apikey": SUPABASE_ANON_KEY},
    json={"email": test_email, "password": new_password},
    timeout=15
)
login_ok = login_new.status_code == 200
print(f"   New password login status: {login_new.status_code} (Success: {login_ok})")

# 5. Verify OLD password is rejected
login_old = requests.post(
    f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
    headers={"apikey": SUPABASE_ANON_KEY},
    json={"email": test_email, "password": orig_password},
    timeout=15
)
old_rejected = login_old.status_code == 400
print(f"   Old password rejected: {old_rejected} (Status: {login_old.status_code})")

# Cleanup
if user_id:
    requests.delete(f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}", headers=headers_admin)
    print(f"\n6. Cleaned up user {user_id}")

print(f"\n===> Blocker 2 Recovery Verdict: {'PASS' if login_ok and old_rejected and len(localhost_leaks) == 0 else 'FAIL'}")
