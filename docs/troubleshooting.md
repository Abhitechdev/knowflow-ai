# KnowFlow AI — Troubleshooting & Incident Runbook

## 1. Fast Diagnostic Matrix

| Symptom | Probable Cause | Diagnostic Command / Check | Resolution |
|---|---|---|---|
| **HTTP 401 Unauthorized on API calls** | Missing or expired JWT token, or incorrect `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Check browser network tab for `Authorization: Bearer <JWT>` header | Re-authenticate at `/login` or check Supabase auth settings |
| **Document upload stuck in PROCESSING** | Background task execution failure or storage network timeout | Query DB: `SELECT id, status, error_message FROM documents ORDER BY created_at DESC;` | Check Render logs for background ingestion worker stack trace |
| **FastEmbed / Embedding model error** | Incompatible embedding model specified in config | Check `EMBEDDING_PROVIDER` and `EMBEDDING_MODEL` in backend environment | Ensure model is supported by FastEmbed (e.g. `BAAI/bge-small-en-v1.5` or `sentence-transformers/all-MiniLM-L6-v2`) or switch to OpenAI |
| **Search returns 0 results** | Document chunks not indexed or query terms below similarity threshold | Inspect `document_chunks` table for target document | Confirm document status is `READY` with `total_chunks > 0` |
| **CORS errors on frontend** | Backend `CORS_ORIGINS` does not match the frontend domain | Check backend `CORS_ORIGINS` setting | Add `https://knowflow-ai-pied.vercel.app` to backend env |
| **Database connection timeout** | Supabase pooler sleeping or direct connection port blocked | Run `curl https://knowflow-ai-4ssd.onrender.com/api/health` | Check `DATABASE_URL` (use port `6543` for connection pooling on Supabase) |

---

## 2. Common Scenarios & Step-by-Step Fixes

### 2.1 Backend Cold Start on Render
- **Behavior**: Initial HTTP request after inactivity takes 15–30 seconds.
- **Cause**: Render free tier instances spin down after 15 minutes of idle time.
- **Mitigation**: Configure an external uptime monitor (e.g., BetterStack or UptimeRobot) to ping `/api/health/live` every 5 minutes to keep the instance warm.

### 2.2 Re-indexing Stalled or Failed Documents
If a document encountered a temporary network glitch during ingestion:
1. Re-upload the document through the web UI or via `POST /api/v1/documents/upload`.
2. The pipeline will overwrite prior failed chunks and re-embed.

### 2.3 Resetting Test Accounts
To clean up residual disposable test accounts created during E2E verification:
```bash
python -c "
import asyncio, httpx, os
from dotenv import dotenv_values
env = dotenv_values('backend/.env')
url = env.get('NEXT_PUBLIC_SUPABASE_URL')
key = env.get('SUPABASE_SERVICE_ROLE_KEY')
async def purge():
    async with httpx.AsyncClient() as c:
        res = await c.get(f'{url}/auth/v1/admin/users', headers={'apikey': key, 'Authorization': f'Bearer {key}'})
        for u in res.json().get('users', []):
            if 'phase6' in u.get('email', ''):
                await c.delete(f'{url}/auth/v1/admin/users/{u[\"id\"]}', headers={'apikey': key, 'Authorization': f'Bearer {key}'})
                print(f'Purged {u[\"email\"]}')
asyncio.run(purge())
"
```
