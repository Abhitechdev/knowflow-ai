# KnowFlow AI — Deployment Guide & Runbook

## 1. Cloud Architecture Overview

KnowFlow AI is deployed across three managed cloud services:
1. **Frontend**: Next.js 14 App Router hosted on **Vercel**.
2. **Backend**: FastAPI (Python 3.11 / Uvicorn) hosted as a Web Service on **Render**.
3. **Database & Storage**: Managed PostgreSQL 16 with `pgvector`, GoTrue Auth, and Storage on **Supabase**.

---

## 2. Production Service Endpoints

| Service | Hosting Provider | URL / Address | Status |
|---|---|---|---|
| **Frontend Application** | Vercel | `https://knowflow-ai-pied.vercel.app` | **Live & Verified** |
| **Backend REST API** | Render | `https://knowflow-ai-4ssd.onrender.com` | **Live & Verified** |
| **Health Check** | Render | `https://knowflow-ai-4ssd.onrender.com/api/health` | **HTTP 200 Healthy** |
| **Liveness Probe** | Render | `https://knowflow-ai-4ssd.onrender.com/api/health/live` | **HTTP 200 Alive** |
| **Readiness Probe** | Render | `https://knowflow-ai-4ssd.onrender.com/api/health/ready` | **HTTP 200 Ready** |
| **Database & Auth** | Supabase | `https://jlbpfgfafobynepeytyl.supabase.co` | **Connected & Verified** |

---

## 3. Deployment Configuration

### 3.1 Vercel Frontend Setup
- **Framework Preset**: Next.js
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `.next`
- **Environment Variables**:
  - `NEXT_PUBLIC_API_URL`: `https://knowflow-ai-4ssd.onrender.com`
  - `NEXT_PUBLIC_SUPABASE_URL`: `https://<project>.supabase.co`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: `<supabase-anon-key>`
  - `NEXT_PUBLIC_SITE_URL`: `https://knowflow-ai-pied.vercel.app`

### 3.2 Render Backend Setup
- **Environment**: Python 3.11
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2`
- **Health Check Path**: `/api/health/live`
- **Environment Variables**:
  - `DATABASE_URL`: `postgresql+asyncpg://...`
  - `DIRECT_DATABASE_URL`: `postgresql://...`
  - `ENVIRONMENT`: `production`
  - `CORS_ORIGINS`: `https://knowflow-ai-pied.vercel.app`
  - `NEXT_PUBLIC_SUPABASE_URL`: `https://<project>.supabase.co`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: `<anon-key>`
  - `SUPABASE_SERVICE_ROLE_KEY`: `<service-role-key>`
  - `LLM_PROVIDER`: `groq` (or `openai`)
  - `EMBEDDING_PROVIDER`: `fastembed` (or `openai`)

### 3.3 Supabase Database Setup
- **Extensions Required**: `pgvector` (`CREATE EXTENSION IF NOT EXISTS vector;`)
- **Storage Buckets**: Private bucket `documents` for raw enterprise files.
- **Migrations**: Executed via Alembic from direct connection:
  ```bash
  alembic upgrade head
  ```

---

## 4. Verification & Smoke Testing Runbook

After any cloud deployment or configuration change:

1. **Verify Root Health**:
   ```bash
   curl -i https://knowflow-ai-4ssd.onrender.com/api/health
   # Must return HTTP 200 {"status": "healthy", "database": {"connected": true}}
   ```

2. **Verify Liveness and Readiness**:
   ```bash
   curl -i https://knowflow-ai-4ssd.onrender.com/api/health/live
   curl -i https://knowflow-ai-4ssd.onrender.com/api/health/ready
   # Both must return HTTP 200
   ```

3. **Verify Fail-Closed Auth**:
   ```bash
   curl -i https://knowflow-ai-4ssd.onrender.com/api/v1/documents
   # Must return HTTP 401 Unauthorized
   ```

4. **Execute Cloud E2E Test Suite**:
   ```bash
   python -u scripts/test_phase6_cloud_e2e.py
   # Must pass all 12 stages with 0 failures
   ```

---

## 5. Rollback Procedures

If a deployment defect is detected:
1. **Frontend Rollback**: In the Vercel Dashboard, select the previous stable deployment (`v0.5.0-phase5-complete` or stable SHA) and click **Promote to Production**.
2. **Backend Rollback**: In Render Dashboard, trigger a rollback to the previous deployment commit or push a revert commit.
3. **Database Migration Downgrade**: If a schema rollback is required:
   ```bash
   alembic downgrade -1
   ```
