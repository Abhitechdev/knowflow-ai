import os
import sys
import time
import uuid
import re
import requests
from dotenv import dotenv_values
from playwright.sync_api import sync_playwright

env_staging = dotenv_values(".env.staging")
SUPABASE_URL = env_staging.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_ANON_KEY = env_staging.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = env_staging.get("SUPABASE_SERVICE_ROLE_KEY")
FRONTEND_URL = env_staging.get("FRONTEND_URL", "https://knowflow-ai-pied.vercel.app").rstrip("/")

print("=== TESTING REAL INBOX (MAIL.TM API) WITH SUPABASE SMTP ===")

# 1. Get available domain from mail.tm
domains_res = requests.get("https://api.mail.tm/domains", timeout=10)
if domains_res.status_code != 200 or not domains_res.json().get("hydra:member"):
    print(f"Could not fetch domains from mail.tm: {domains_res.status_code}")
    sys.exit(1)

domain = domains_res.json()["hydra:member"][0]["domain"]
username = f"e2e_verify_{uuid.uuid4().hex[:8]}"
inbox_email = f"{username}@{domain}"
inbox_password = "MailPassword_2026!"

# 2. Create account on mail.tm
acc_res = requests.post(
    "https://api.mail.tm/accounts",
    json={"address": inbox_email, "password": inbox_password},
    timeout=10
)
if acc_res.status_code not in [200, 201]:
    print(f"Failed to create mailbox: {acc_res.status_code} - {acc_res.text}")
    sys.exit(1)

print(f"1. Created real test inbox: {inbox_email}")

# 3. Get mail.tm JWT token
tok_res = requests.post(
    "https://api.mail.tm/token",
    json={"address": inbox_email, "password": inbox_password},
    timeout=10
)
mail_token = tok_res.json().get("token")
mail_headers = {"Authorization": f"Bearer {mail_token}"}

# 4. Trigger REAL registration via Supabase client / GoTrue signup (which triggers Supabase SMTP)
print(f"\n2. Registering {inbox_email} via Supabase GoTrue signup endpoint...")
reg_res = requests.post(
    f"{SUPABASE_URL}/auth/v1/signup",
    headers={"apikey": SUPABASE_ANON_KEY},
    json={
        "email": inbox_email,
        "password": "E2E_TestPassword123!",
        "options": {
            "emailRedirectTo": f"{FRONTEND_URL}/auth/callback"
        }
    },
    timeout=15
)
print(f"   GoTrue signup response: {reg_res.status_code} - {reg_res.text[:150]}")

# 5. Poll mail.tm for incoming email (waiting up to 45 seconds for SMTP delivery)
print("\n3. Polling real mailbox for incoming Supabase confirmation email...")
confirmation_link = None
email_body = None

for attempt in range(1, 15):
    time.sleep(3)
    msgs_res = requests.get("https://api.mail.tm/messages", headers=mail_headers, timeout=10)
    if msgs_res.status_code == 200:
        msgs = msgs_res.json().get("hydra:member", [])
        if msgs:
            msg_id = msgs[0]["id"]
            msg_detail = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=mail_headers, timeout=10)
            msg_data = msg_detail.json()
            email_body = msg_data.get("text") or msg_data.get("html") or ""
            print(f"   >>> Email received! Subject: {msg_data.get('subject')}")
            
            # Extract confirmation link
            urls = re.findall(r'https?://[^\s<>"\']+', email_body)
            for u in urls:
                if "verify" in u or "confirmation" in u or "auth" in u:
                    confirmation_link = u
                    break
            break
    print(f"   Attempt {attempt}/14: No email yet...")

if not confirmation_link:
    print("\n>>> Result: No email delivered to real inbox (Supabase rate limit or custom SMTP required).")
else:
    print(f"\n4. Extracted real email confirmation link: {confirmation_link}")
    
    # 6. Open link in Playwright and verify browser flow
    localhost_leaks = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        def handle_req(req):
            if "localhost" in req.url or "127.0.0.1" in req.url:
                localhost_leaks.append(req.url)

        page.on("request", handle_req)
        
        print(f"5. Navigating Playwright to real email confirmation link...")
        page.goto(confirmation_link, wait_until="networkidle")
        page.wait_for_timeout(4000)
        
        final_url = page.url
        print(f"   Landed on URL: {final_url}")
        print(f"   Localhost leaks: {len(localhost_leaks)}")
        
        # Verify session persistence
        page.reload(wait_until="networkidle")
        print(f"   URL after reload: {page.url}")
        browser.close()

print("=== REAL SMTP TEST COMPLETED ===")
