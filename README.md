# KnowFlow AI — Enterprise Knowledge & SOP Agent

> **"Turn company documents into reliable, searchable knowledge."**

KnowFlow AI is a full-stack RAG (Retrieval-Augmented Generation) platform for enterprise document intelligence. Employees query SOPs, policies, and technical manuals in natural language and receive **grounded, citation-backed answers** — the system refuses to fabricate answers outside the authorized document corpus.

---

## Benchmark Results (Curated 15-Case Dataset)

> The following metrics reflect performance on a controlled 15-case benchmark curated from the demo document set. These are engineering validation results — not universal open-domain performance claims.

| Metric | Value |
|--------|-------|
| NDCG@5 | **0.9210** |
| MRR | **0.8939** |
| False Positives (hallucinations accepted) | **0** |
| False Negatives (grounded answers refused) | **0** |
| Benchmark pass rate | **15/15** |
| Automated test suite | **68/68 passing** |

---

## Core Features

- **Hybrid Retrieval**: Dense embeddings (OpenAI) + BM25 sparse search fused via Reciprocal Rank Fusion.
- **HybridReranker**: Heuristic BM25 + semantic score fusion — low-latency alternative to neural cross-encoders for controlled enterprise corpora.
- **Grounded Answering Policy**: Answers require retrieved document support. Out-of-scope queries are refused — never hallucinated.
- **Citation-backed Responses**: Every answer includes document name, section, and supporting text excerpt.
- **Prompt Injection Guardrails**: Pattern-based detection blocks instruction injection attempts.
- **Role-Based Access Control**: ADMIN > MANAGER > EMPLOYEE roles with document clearance levels (INTERNAL, CONFIDENTIAL, RESTRICTED).
- **Audit Logging**: Every query logged with user ID, workspace, timestamp — auditability foundations relevant to regulated environments.
- **Rate Limiting**: Sliding-window rate limiter on the chat endpoint.
- **Production Auth**: Supabase JWT — fail-closed in production (HTTP 401 if token absent/invalid).

---

## Architecture

```
Document Upload
    → Text Extraction (TXT, PDF, DOCX, MD)
    → Semantic Chunking (configurable overlap + size)
    → Dense Embedding (OpenAI text-embedding-3-small)
    → Sparse Indexing (BM25)
    → Stored in PostgreSQL + pgvector

User Query
    → Prompt Injection Guardrails
    → Hybrid Retrieval (Dense + BM25 via RRF fusion)
    → HybridReranker (heuristic BM25 + semantic score fusion)
    → Grounded Answering Policy
    → LLM Answer Generation (context-only, citations required)
    → Structured Response with Citations
```

```
┌─────────────────────────────────────┐
│    Next.js 14 Frontend              │
│    (TypeScript, Tailwind, Supabase) │
└───────────────┬─────────────────────┘
                │ REST API (33 endpoints)
                ▼
┌─────────────────────────────────────┐
│    FastAPI Backend (Python 3.11)    │
│    Async SQLAlchemy · pgvector      │
│    JWT Auth · RBAC · Rate Limiting  │
└──────────┬────────────┬─────────────┘
           │            │
    ┌──────▼──────┐  ┌──▼──────────┐
    │ PostgreSQL   │  │ Supabase    │
    │ + pgvector   │  │ Auth/Storage│
    └─────────────┘  └─────────────┘
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Backend | Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0 Async |
| Database | PostgreSQL 16 + pgvector (Supabase managed) |
| Auth | Supabase Auth (fail-closed JWT in production) |
| Embeddings | OpenAI text-embedding-3-small |
| LLM | OpenAI gpt-4o-mini (configurable provider) |
| Testing | pytest, pytest-asyncio (68 tests) |
| Containers | Docker (python:3.11-slim), Docker Compose |
| CI/CD | GitHub Actions (lint, test, gitleaks, trivy, deploy) |

---

## Quick Start

### Local Development (Native)

```powershell
# 1. Copy and fill environment
cp backend/.env.production.example backend/.env
# Edit backend/.env with your OpenAI key, Supabase credentials

# 2. Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --app-dir ../backend --reload --port 8000

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### Docker (Production-Parity)

```bash
# Build and run all services
docker compose -f docker-compose.prod.yml up --build

# With local PostgreSQL (for offline development)
docker compose -f docker-compose.prod.yml --profile local-db up --build

# With optional Nginx reverse proxy
docker compose -f docker-compose.prod.yml --profile with-nginx up --build
```

### Run Tests

```powershell
$env:PYTHONPATH="backend"; pytest backend/tests -v
# 68 passed
```

---

## Project Structure

```
ragproject/
├── backend/
│   ├── app/
│   │   ├── auth/            # Fail-closed JWT auth + RBAC
│   │   ├── core/            # Config, Sentry, security headers
│   │   ├── rag/             # Hybrid retrieval, HybridReranker, grounding policy
│   │   ├── evaluation/      # NDCG, MRR, faithfulness metrics
│   │   ├── api/v1/          # REST endpoints (33 total)
│   │   └── main.py          # FastAPI app (Sentry, CORS, security headers)
│   ├── tests/               # 68 automated tests
│   ├── Dockerfile           # python:3.11-slim, non-root, configurable workers
│   └── .env.production.example
├── frontend/
│   ├── src/                 # Next.js 14 App Router pages & components
│   ├── Dockerfile           # Node 20 multi-stage, standalone output
│   └── .env.production.example
├── scripts/
│   ├── production_smoke_test.py   # Staging-first smoke test harness
│   ├── backup_db.py               # Automated pg_dump backup
│   ├── test_restore.py            # Actual restore verification (RTO ≤ 30 min target)
│   ├── export_openapi.py          # OpenAPI 3.1 spec exporter
│   └── audit_security.py          # Secret/credential audit script
├── docs/
│   ├── openapi.json               # Full OpenAPI 3.1 spec (33 endpoints)
│   ├── architecture.md            # System architecture guide
│   ├── disaster_recovery.md       # Backup, restore, failover runbook
│   ├── portfolio_case_study.md    # Engineering case study & resume highlights
│   └── demo_guide.md              # Live demo walkthrough script
├── .github/workflows/ci-cd.yml   # Full CI/CD pipeline
├── docker-compose.prod.yml        # Production-parity container orchestration
└── deploy/nginx.conf              # Optional Nginx reverse proxy config
```

---

## Security

- **Production JWT**: Fail-closed (HTTP 401 if token absent or invalid). Test bypass only in `development`/`test` environments.
- **Admin RBAC**: All `/admin` endpoints require verified ADMIN role (HTTP 403 otherwise).
- **CORS**: Explicit origin allowlist. No wildcards.
- **Security Headers**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy (production).
- **Secret Detection**: gitleaks in CI/CD pipeline.
- **Container Scanning**: trivy in CI/CD pipeline.
- **Dependency Audit**: pip-audit (backend) + npm audit (frontend) in CI/CD.

---

## Disaster Recovery

| Metric | Target |
|--------|--------|
| RTO (Recovery Time Objective) | ≤ 30 minutes |
| RPO (Recovery Point Objective) | ≤ 1 hour |

Targets validated by `scripts/test_restore.py` (actual backup → restore cycle). See [`docs/disaster_recovery.md`](docs/disaster_recovery.md).

---

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/openapi.json`](docs/openapi.json) | OpenAPI 3.1 specification (33 endpoints, 24 schemas) |
| [`docs/architecture.md`](docs/architecture.md) | System architecture and data flow |
| [`docs/disaster_recovery.md`](docs/disaster_recovery.md) | Backup, restore, and failover runbook |
| [`docs/portfolio_case_study.md`](docs/portfolio_case_study.md) | Engineering case study and resume highlights |
| [`docs/demo_guide.md`](docs/demo_guide.md) | Interactive demo walkthrough |
