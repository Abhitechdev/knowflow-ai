import os
import sys
import time
import uuid
import requests
from dotenv import dotenv_values

env_staging = dotenv_values(".env.staging")
SUPABASE_URL = env_staging.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_ANON_KEY = env_staging.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = env_staging.get("SUPABASE_SERVICE_ROLE_KEY")
BACKEND_URL = env_staging.get("BACKEND_URL", "https://knowflow-ai-4ssd.onrender.com").rstrip("/")

print("=== BLOCKER 1: TESTING AUTHENTICATED CLOUD RATE LIMITING ===")
print(f"Backend URL: {BACKEND_URL}")

# Create / authenticate test user
headers_admin = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
}

test_id = uuid.uuid4().hex[:6]
email = f"ratelimit_e2e_{test_id}@testflow.io"
password = "SecurePassword123!"

# 1. Create confirmed user
u_res = requests.post(
    f"{SUPABASE_URL}/auth/v1/admin/users",
    headers=headers_admin,
    json={"email": email, "password": password, "email_confirm": True},
    timeout=15
)
user_data = u_res.json()
user_id = user_data.get("id")
print(f"1. Created test user: {email} (ID: {user_id})")

# 2. Login to get valid JWT
tok_res = requests.post(
    f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
    headers={"apikey": SUPABASE_ANON_KEY},
    json={"email": email, "password": password},
    timeout=15
)
tok_data = tok_res.json()
jwt_token = tok_data.get("access_token")
print(f"2. Acquired valid JWT token: {jwt_token[:30]}...")

auth_headers = {
    "Authorization": f"Bearer {jwt_token}"
}

# 3. Create workspace for this user
ws_res = requests.post(
    f"{BACKEND_URL}/api/v1/workspaces",
    headers=auth_headers,
    json={
        "name": f"RateLimit WS {test_id}",
        "slug": f"ratelimit-ws-{test_id}"
    },
    timeout=15
)
print(f"3. Workspace creation status: {ws_res.status_code}")
if ws_res.status_code in [200, 201]:
    ws_id = ws_res.json().get("id")
    print(f"   Workspace ID: {ws_id}")

# 4. Perform burst requests to /api/v1/search (Configured limit: 60 req/min)
print("\n4. Sending sequential requests to /api/v1/search (Threshold: 60 req/min)...")
status_sequence = []
retry_after_header = None
rate_limit_triggered = False
trigger_index = -1
start_time = time.time()

for i in range(1, 75):
    r = requests.get(
        f"{BACKEND_URL}/api/v1/search?query=test_ratelimit_token",
        headers=auth_headers,
        timeout=10
    )
    status_sequence.append(r.status_code)
    if r.status_code == 429:
        rate_limit_triggered = True
        trigger_index = i
        retry_after_header = r.headers.get("Retry-After")
        print(f"   >>> Request #{i}: HTTP 429 TOO MANY REQUESTS! Retry-After: {retry_after_header}s")
        print(f"   >>> Body: {r.text}")
        break
    elif i % 10 == 0 or i == 1:
        print(f"   Request #{i}: HTTP {r.status_code}")

elapsed = time.time() - start_time
print(f"\nSummary:")
print(f"  - Total requests sent: {len(status_sequence)}")
print(f"  - Status distribution: { {s: status_sequence.count(s) for s in set(status_sequence)} }")
print(f"  - Rate limit triggered: {rate_limit_triggered} at request #{trigger_index}")
print(f"  - Elapsed time: {elapsed:.2f}s")

# Cleanup user
if user_id:
    requests.delete(f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}", headers=headers_admin)
    print(f"\n5. Cleaned up test user {user_id}")

print("=== TEST COMPLETE ===")
