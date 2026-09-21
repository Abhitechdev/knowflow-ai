import os
import sys
import time
import uuid
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import dotenv_values

env_staging = dotenv_values(".env.staging")
SUPABASE_URL = env_staging.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_ANON_KEY = env_staging.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = env_staging.get("SUPABASE_SERVICE_ROLE_KEY")
BACKEND_URL = env_staging.get("BACKEND_URL", "https://knowflow-ai-4ssd.onrender.com").rstrip("/")

print("=== CONCURRENT CLOUD RATE LIMITING TEST ===")
print(f"Backend URL: {BACKEND_URL}")

headers_admin = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
}

test_id = uuid.uuid4().hex[:6]
email = f"ratelimit_concurrent_{test_id}@testflow.io"
password = "SecurePassword123!"

# 1. Create confirmed user
u_res = requests.post(
    f"{SUPABASE_URL}/auth/v1/admin/users",
    headers=headers_admin,
    json={"email": email, "password": password, "email_confirm": True},
    timeout=15
)
user_id = u_res.json().get("id")

# 2. Login to get valid JWT
tok_res = requests.post(
    f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
    headers={"apikey": SUPABASE_ANON_KEY},
    json={"email": email, "password": password},
    timeout=15
)
jwt_token = tok_res.json().get("access_token")
auth_headers = {"Authorization": f"Bearer {jwt_token}"}

# 3. Create workspace
ws_res = requests.post(
    f"{BACKEND_URL}/api/v1/workspaces",
    headers=auth_headers,
    json={"name": f"Concurrent WS {test_id}", "slug": f"concurrent-ws-{test_id}"},
    timeout=15
)
print(f"Workspace created: {ws_res.status_code}")

# 4. Burst 75 concurrent requests within < 10 seconds
print("\nFiring 75 concurrent requests to /api/v1/search...")

def send_search_req(req_num):
    try:
        r = requests.get(
            f"{BACKEND_URL}/api/v1/search?query=test_concurrent_ratelimit",
            headers=auth_headers,
            timeout=15
        )
        return req_num, r.status_code, r.headers.get("Retry-After"), r.text[:120]
    except Exception as e:
        return req_num, f"ERR: {e}", None, ""

start_time = time.time()
results = []
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(send_search_req, i) for i in range(1, 76)]
    for f in as_completed(futures):
        results.append(f.result())

elapsed = time.time() - start_time
results.sort(key=lambda x: x[0])

status_counts = {}
limit_429s = []
for req_num, status, retry_after, body in results:
    status_counts[status] = status_counts.get(status, 0) + 1
    if status == 429:
        limit_429s.append((req_num, retry_after, body))

print(f"\nBurst Execution Summary:")
print(f"  - Total Requests: {len(results)}")
print(f"  - Elapsed Time: {elapsed:.2f}s (All inside 60s sliding window)")
print(f"  - Status Distribution: {status_counts}")

if limit_429s:
    print(f"\n>>> SUCCESS: Rate limit triggered! Total 429 responses: {len(limit_429s)}")
    print(f"  Sample 429 -> Request #{limit_429s[0][0]}, Retry-After: {limit_429s[0][1]}s, Body: {limit_429s[0][2]}")
else:
    print(f"\n>>> Rate limit NOT triggered (No 429s). Deployed commit on Render may not have rate limiting middleware.")

# Cleanup
if user_id:
    requests.delete(f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}", headers=headers_admin)
    print(f"\nCleaned up user {user_id}")
