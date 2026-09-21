import requests
import os
import sys
import time

FRONTEND_URL = "https://knowflow-ai-pied.vercel.app"
BACKEND_URL = "https://knowflow-ai-4ssd.onrender.com"

results = []

def record(test_name, status, details=""):
    results.append({
        "test": test_name,
        "status": status,
        "details": details
    })
    print(f"[{status}] {test_name}: {details}")

def test_backend_health():
    try:
        resp = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("environment") == "staging":
                record("Backend Health", "PASS", f"200 OK, environment is staging. db: {data.get('database')}")
            else:
                record("Backend Health", "FAIL", f"Environment is {data.get('environment')}, expected staging")
        else:
            record("Backend Health", "FAIL", f"Status code {resp.status_code}")
    except Exception as e:
        record("Backend Health", "FAIL", str(e))

if __name__ == "__main__":
    test_backend_health()
