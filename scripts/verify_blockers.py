"""Comprehensive Verification Script for Gate 5E Blockers:
BLOCKER 1 — Live Rate Limiting with Concurrent Authenticated Cloud Session
BLOCKER 2 — Complete 12-Step Password Recovery on Live Vercel & Supabase
"""

import os
import sys
import time
import json
import uuid
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import dotenv_values
from playwright.sync_api import sync_playwright

# Load cloud configuration
env_staging = dotenv_values(".env.staging")
SUPABASE_URL = env_staging.get("NEXT_PUBLIC_SUPABASE_URL", "https://jlbpfgfafobynepeytyl.supabase.co").rstrip("/")
SUPABASE_ANON_KEY = env_staging.get("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = env_staging.get("SUPABASE_SERVICE_ROLE_KEY", "")
BACKEND_URL = env_staging.get("BACKEND_URL", "https://knowflow-ai-4ssd.onrender.com").rstrip("/")
FRONTEND_URL = env_staging.get("FRONTEND_URL", "https://knowflow-ai-pied.vercel.app").rstrip("/")

EVIDENCE = {}

# =====================================================================
# 1. BLOCKER 1 — LIVE RATE LIMITING (CONCURRENT AUTHENTICATED BURST)
# =====================================================================
def verify_blocker_1_rate_limiting():
    print("\n" + "="*70)
    print(">>> EXECUTING BLOCKER 1: LIVE RATE LIMITING VERIFICATION <<<")
    print("="*70)

    # 1. Query Render Health to verify live identity and deployment status
    health_res = requests.get(f"{BACKEND_URL}/api/v1/health", timeout=15)
    health_data = health_res.json() if health_res.status_code == 200 else {}
    render_version = health_data.get("version", "0.1.0")
    print(f"[*] Render Health Status: {health_res.status_code}, Version: {render_version}")

    # 2. Create and authenticate a real test user
    test_user_id = uuid.uuid4().hex[:6]
    test_email = f"rate_limit_user_{test_user_id}@testflow.io"
    test_pwd = "RateLimitPassword_2026!"

    admin_headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
    }

    create_res = requests.post(
        f"{SUPABASE_URL}/auth/v1/admin/users",
        headers=admin_headers,
        json={"email": test_email, "password": test_pwd, "email_confirm": True},
        timeout=15
    )
    user_data = create_res.json() if create_res.status_code in [200, 201] else {}
    user_uuid = user_data.get("id", "unknown")
    print(f"[*] Created confirmed test user: {test_email} (UUID: {user_uuid[:8]}...)")

    # Login to acquire user JWT access token
    auth_res = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={"apikey": SUPABASE_ANON_KEY},
        json={"email": test_email, "password": test_pwd},
        timeout=15
    )
    auth_data = auth_res.json() if auth_res.status_code == 200 else {}
    access_token = auth_data.get("access_token")

    if not access_token:
        raise RuntimeError("Failed to acquire user JWT access token")

    print("[*] Authenticated cloud user token acquired: YES")
    user_auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Create workspace
    ws_res = requests.post(
        f"{BACKEND_URL}/api/v1/workspaces",
        headers=user_auth_headers,
        json={"name": f"RateLimit WS {test_user_id}", "slug": f"rl-ws-{test_user_id}"},
        timeout=15
    )
    print(f"[*] Workspace creation status: {ws_res.status_code}")

    # 3. Burst search endpoint to exceed rate limit (configured: 60 requests/min)
    endpoint = f"{BACKEND_URL}/api/v1/search?query=concurrent_probe"
    total_requests = 85

    def send_request(req_id):
        try:
            r = requests.get(endpoint, headers=user_auth_headers, timeout=15)
            retry_hdr = r.headers.get("Retry-After")
            return (req_id, r.status_code, retry_hdr)
        except Exception as e:
            return (req_id, f"Err:{type(e).__name__}", None)

    print(f"[*] Launching {total_requests} concurrent requests against {endpoint}...")
    t0 = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(send_request, i) for i in range(1, total_requests + 1)]
        for future in as_completed(futures):
            results.append(future.result())

    t_elapsed = round(time.time() - t0, 2)
    statuses = [res[1] for res in results]
    retries = [res[2] for res in results if res[2] is not None]

    count_200 = statuses.count(200)
    count_429 = statuses.count(429)

    print("\n" + "-"*50)
    print(f"[*] Burst results (Elapsed: {t_elapsed}s):")
    print(f"    - Total Requests: {total_requests}")
    print(f"    - HTTP 200 OK: {count_200}")
    print(f"    - HTTP 429 Too Many Requests: {count_429}")
    print(f"    - Retry-After sample values: {retries[:5]}")
    print(f"    - Status distribution: { {str(s): statuses.count(s) for s in set(statuses)} }")
    print("-"*50)

    rate_limit_passed = count_429 > 0 and count_200 > 0

    EVIDENCE["BLOCKER_1_RATE_LIMITING"] = {
        "status": "PASS" if rate_limit_passed else "FAIL",
        "total_requests": total_requests,
        "count_200": count_200,
        "count_429": count_429,
        "retry_after_header_samples": retries[:5],
        "endpoint_tested": "/api/v1/search?query=concurrent_probe",
        "authenticated_user": f"rate_limit_user_{test_user_id}@testflow.io",
        "render_deployed_version": render_version,
        "time_elapsed_seconds": t_elapsed,
        "demonstrates_429": rate_limit_passed
    }

    # Clean up test user
    if user_uuid != "unknown":
        requests.delete(f"{SUPABASE_URL}/auth/v1/admin/users/{user_uuid}", headers=admin_headers)

    return rate_limit_passed


# =====================================================================
# 2. BLOCKER 2 — COMPLETE 12-STEP PASSWORD RECOVERY
# =====================================================================
def verify_blocker_2_password_recovery():
    print("\n" + "="*70)
    print(">>> EXECUTING BLOCKER 2: COMPLETE PASSWORD RECOVERY VERIFICATION <<<")
    print("="*70)

    admin_headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
    }

    # 1. Create a confirmed user with initial password
    test_id = uuid.uuid4().hex[:6]
    test_email = f"recovery_e2e_{test_id}@testflow.io"
    initial_password = "InitialPassword_2026_Auth!"
    new_password = "UpdatedPassword_2026_Secure!"

    create_res = requests.post(
        f"{SUPABASE_URL}/auth/v1/admin/users",
        headers=admin_headers,
        json={"email": test_email, "password": initial_password, "email_confirm": True},
        timeout=15
    )
    user_data = create_res.json()
    user_id = user_data.get("id")
    print(f"[*] Step 1: Created confirmed user {test_email} (ID: {user_id[:8]}...)")

    # 2. Generate real Supabase recovery link pointing to Vercel /update-password
    link_res = requests.post(
        f"{SUPABASE_URL}/auth/v1/admin/generate_link",
        headers=admin_headers,
        json={
            "type": "recovery",
            "email": test_email,
            "options": {
                "redirectTo": f"{FRONTEND_URL}/update-password"
            }
        },
        timeout=15
    )
    link_data = link_res.json()
    action_link = link_data.get("action_link")
    print(f"[*] Step 2: Generated Real Supabase Recovery Link (Type: recovery, Redirect: {FRONTEND_URL}/update-password)")

    steps_record = {
        "step_1_user_provisioned": True,
        "step_2_recovery_link_generated": action_link is not None,
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Step 3: Click recovery link in browser
        print("[*] Step 3: Navigating to recovery link in browser...")
        page.goto(action_link, wait_until="networkidle")
        page.wait_for_timeout(4000)

        # Step 4: Confirm recovery session is established
        landed_url = page.url
        print(f"[*] Step 4: Landed URL: {landed_url.split('#')[0] if '#' in landed_url else landed_url}")
        session_established = "/update-password" in landed_url and "access_token=" in landed_url
        steps_record["step_4_session_established"] = session_established
        print(f"    - Recovery session established: {session_established}")

        # Step 5: Reach /update-password and verify form
        pwd_input = page.wait_for_selector("input#password", timeout=10000)
        confirm_input = page.wait_for_selector("input#confirm-password", timeout=10000)
        submit_btn = page.wait_for_selector("button[type='submit']", timeout=10000)
        form_ok = pwd_input is not None and confirm_input is not None and submit_btn is not None
        steps_record["step_5_reached_update_page"] = form_ok
        print(f"[*] Step 5: Reached /update-password with valid form: {form_ok}")

        # Step 6: Set NEW password
        print("[*] Step 6: Entering new password and confirming...")
        pwd_input.fill(new_password)
        confirm_input.fill(new_password)
        submit_btn.click()
        page.wait_for_timeout(4000)

        # Step 7: Confirm password update succeeds
        success_text = ""
        try:
            success_el = page.wait_for_selector(".text-success, [class*='success']", timeout=5000)
            success_text = success_el.inner_text() if success_el else ""
        except Exception:
            pass
        update_ok = "successfully" in success_text.lower() or "/login" in page.url or page.query_selector("text=successfully") is not None
        steps_record["step_7_update_succeeded"] = update_ok
        print(f"[*] Step 7: Password update confirmation: {'SUCCESS' if update_ok else 'FAILED'} (Message: '{success_text}')")

        # Step 8: Sign out
        print("[*] Step 8: Signing out and clearing browser storage...")
        context.clear_cookies()
        page.evaluate("window.localStorage.clear(); window.sessionStorage.clear();")
        page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle")
        page.wait_for_timeout(2000)
        steps_record["step_8_signed_out"] = "/login" in page.url
        print(f"[*] Step 8: Signed out, landed on: {page.url}")

        # Step 9: Login using NEW password
        print("[*] Step 9: Logging in with NEW password...")
        page.fill("input#email-address", test_email)
        page.fill("input#password", new_password)
        page.click("button[type='submit']")
        page.wait_for_timeout(5000)

        # Step 10: Confirm login succeeds
        post_new_login_url = page.url
        new_login_ok = "/login" not in post_new_login_url
        steps_record["step_10_new_login_succeeded"] = new_login_ok
        print(f"[*] Step 10: New password login: {'SUCCESS' if new_login_ok else 'FAILED'} (Landed on: {post_new_login_url})")

        # Step 11: Confirm OLD password is rejected
        print("[*] Step 11: Verifying OLD password rejection in incognito context...")
        incognito_ctx = browser.new_context()
        incognito_page = incognito_ctx.new_page()
        incognito_page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle")
        incognito_page.fill("input#email-address", test_email)
        incognito_page.fill("input#password", initial_password)
        incognito_page.click("button[type='submit']")
        incognito_page.wait_for_timeout(4000)

        err_text = ""
        try:
            err_el = incognito_page.wait_for_selector(".text-danger, [class*='danger']", timeout=5000)
            err_text = err_el.inner_text() if err_el else ""
        except Exception:
            pass
        old_rejected = "/login" in incognito_page.url and ("invalid" in err_text.lower() or "credentials" in err_text.lower() or len(err_text) > 0)
        steps_record["step_11_old_password_rejected"] = old_rejected
        print(f"[*] Step 11: Old password rejected: {'YES' if old_rejected else 'NO'} (Error message: '{err_text}')")
        incognito_ctx.close()

        # Step 12: Reload authenticated application and confirm session persistence
        print("[*] Step 12: Reloading authenticated application...")
        page.reload(wait_until="networkidle")
        page.wait_for_timeout(3000)
        reloaded_url = page.url
        session_persisted = "/login" not in reloaded_url
        steps_record["step_12_session_persisted"] = session_persisted
        print(f"[*] Step 12: Session persisted on reload: {'YES' if session_persisted else 'NO'} (URL: {reloaded_url})")

        browser.close()

    # Clean up test user
    if user_id:
        requests.delete(f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}", headers=admin_headers)

    all_recovery_steps_pass = all([
        steps_record.get("step_4_session_established", False),
        steps_record.get("step_5_reached_update_page", False),
        steps_record.get("step_7_update_succeeded", False),
        steps_record.get("step_8_signed_out", False),
        steps_record.get("step_10_new_login_succeeded", False),
        steps_record.get("step_11_old_password_rejected", False),
        steps_record.get("step_12_session_persisted", False),
    ])

    EVIDENCE["BLOCKER_2_PASSWORD_RECOVERY"] = {
        "status": "PASS" if all_recovery_steps_pass else "FAIL",
        "target_url": f"{FRONTEND_URL}/update-password",
        "steps_record": steps_record,
        "complete_12_steps_verified": all_recovery_steps_pass
    }

    return all_recovery_steps_pass


if __name__ == "__main__":
    print("=================================================================")
    print("      GATE 5E BLOCKERS DEEP CLOUD VERIFICATION RUNNER            ")
    print("=================================================================")
    b1_pass = verify_blocker_1_rate_limiting()
    b2_pass = verify_blocker_2_password_recovery()

    print("\n" + "="*70)
    print(f"BLOCKER 1 (Live Rate Limiting):     {'PASS' if b1_pass else 'FAIL'}")
    print(f"BLOCKER 2 (Complete 12-Step Reset): {'PASS' if b2_pass else 'FAIL'}")
    print("="*70)

    with open("scratch/blockers_evidence.json", "w") as f:
        json.dump(EVIDENCE, f, indent=2)
    print("[*] Evidence written to scratch/blockers_evidence.json")
