# KnowFlow AI — Enterprise Knowledge & SOP Assistant

> **"Turn company SOPs, manuals, and policies into reliable, citation-backed intelligence."**

KnowFlow AI is a production-engineered Full-Stack Retrieval-Augmented Generation (RAG) platform designed for enterprise document intelligence. It enables employees to query standard operating procedures (SOPs), safety guidelines, regulatory manuals, and company policies in natural language, delivering **grounded, citation-backed answers** with strict tenant isolation, fail-closed authentication, and role-based access control (RBAC).

---

## 1. Executive Summary & Problem Solved

Modern organizations face severe operational friction:
- **Scattered Institutional Knowledge**: Critical operating procedures and compliance rules are trapped in siloed PDFs, Word documents, and intranet directories.
- **LLM Hallucination Risk**: Generic AI chatbots fabricate plausible-sounding facts, exposing organizations to compliance, safety, and operational hazards.
- **Access Control & Data Leakage**: Traditional search lacks granular document clearance levels (e.g., CONFIDENTIAL vs. RESTRICTED).

**KnowFlow AI solves this** by coupling a multi-stage Hybrid Retrieval Engine (Dense pgvector + Sparse BM25 fused via Reciprocal Rank Fusion) with strict server-side authorization and a fail-closed Grounded Answering Policy. If retrieved documentation lacks supporting evidence, KnowFlow refuses to speculate.

---

## 2. Benchmark Results & Verification Metrics

> **Note on Methodology**: Metrics reflect evaluation on a curated 15-case engineering benchmark derived from realistic compliance and SOP document sets. These metrics represent reproducible engineering benchmarks rather than universal open-domain claims.

| Benchmark / Quality Metric | Value / Scope | Verification Status |
|---|---|---|
| **Hit@1** | **81.8%** | Verified (Benchmark Suite) |
| **Hit@3** | **100.0%** | Verified (Benchmark Suite) |
| **Hit@5** | **100.0%** | Verified (Benchmark Suite) |
| **MRR (Mean Reciprocal Rank)** | **0.8939** | Verified (Benchmark Suite) |
| **NDCG@5** | **0.9210** | Verified (Benchmark Suite) |
| **Automated Backend Regression** | **88 / 88 Passing (100%)** | Verified (`pytest backend/tests`) |
| **OpenAPI Contract Drift** | **0 Divergences (34 routes / 26 schemas)** | Verified (`test_openapi_contract_drift.py`) |
| **Database Restore Verification** | **28.08s (16/16 tables, SHA-256 parity)** | Verified (Gate 5F-2 Test Suite) |

---

## 3. High-Level & Component Architecture

```
                                 ┌─────────────────────────────────┐
                                 │       Next.js 14 Frontend       │
                                 │ (TypeScript, Tailwind, Supabase)│
                                 │ https://knowflow-ai-pied.vercel.app │
                                 └───────────────┬─────────────────┘
                                                 │ HTTPS / JSON (Bearer JWT)
                                                 ▼
                                 ┌─────────────────────────────────┐
                                 │   FastAPI Backend (Python 3.11) │
                                 │ https://knowflow-ai-4ssd.onrender.com │
                                 └───────┬───────────────┬─────────┘
                                         │               │
                        ┌────────────────▼──┐         ┌──▼───────────────┐
                        │ Supabase Database │         │ Supabase Storage │
                        │  PostgreSQL 16    │         │  Private Bucket  │
                        │    + pgvector     │         │ (Encrypted SOPs) │
                        └───────────────────┘         └──────────────────┘
```

### Detailed Ingestion & RAG Flow

```
[Document Upload (PDF/DOCX/TXT/MD/CSV)]
   │
   ▼
[Supabase Private Storage Ingestion]
   │
   ▼
[Background Extraction & Semantic Chunking (500 tokens, 10% overlap)]
   │
   ▼
[Dense Embedding (FastEmbed/OpenAI) + Sparse BM25 Indexing]
   │
   ▼
[PostgreSQL pgvector Vector Storage + Document Metadata]

---------------------------------------------------------------------------------

[User Natural Language Query]
   │
   ▼
[Fail-Closed JWT Validation & Workspace Context Resolution]
   │
   ▼
[Prompt Injection & Jailbreak Heuristic Inspection]
   │
   ▼
[Hybrid Retrieval (Dense cosine similarity + Sparse BM25)]
   │
   ▼
[Reciprocal Rank Fusion (RRF k=60) + Hybrid Reranking]
   │
   ▼
[RBAC Document Clearance & Tenant Isolation Filter]
   │
   ▼
[Grounded LLM Synthesis (Strict Context Constraint)]
   │
   ▼
[Response Formatter with Citations & Source Excerpts]
```

---

## 4. Core Features

- **Hybrid Dense + Sparse Search**: Fuses pgvector cosine similarity with BM25 keyword matching via Reciprocal Rank Fusion (RRF) to capture both exact domain terms and semantic intent.
- **Fail-Closed Grounded Answering**: Enforces strict context prompting. If context is absent, the model returns a standard grounded refusal instead of hallucinating.
- **Exact-Match Citations**: Every generated statement includes document title, section heading, page number, and source excerpt.
- **Multi-Tenant Workspace Isolation**: Organization and workspace boundaries are enforced strictly at database query level using verified token claims.
- **Role-Based Access Control (RBAC)**: Supports roles (`ADMIN`, `MANAGER`, `EMPLOYEE`, `COMPLIANCE_OFFICER`, `AUDITOR`) and clearance classifications (`PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`).
- **Prompt Injection Defense**: Multi-pattern regex and delimiter sanitization detect instruction override attempts.
- **Sliding-Window Rate Limiting**: Request-rate caps on chat and search endpoints protect backend resources.
- **Hard Deletion & Storage Cascade**: Complete atomic purging of document records, chunks, permissions, and cloud storage files.
- **Audit Logging**: Structured audit trail tracking logins, document uploads, and deletions.
- **Disaster Recovery & Migrations**: Version-controlled Alembic migrations and verified backup/restore automation.

---

## 5. Security & Authentication Architecture

1. **Fail-Closed JWT Enforcement**: In production (`ENVIRONMENT=production`), all API endpoints require a valid Supabase JWT Bearer token. Unauthenticated requests are rejected immediately with `HTTP 401 Unauthorized`.
2. **Server-Side Tenant Resolution**: Workspace ID and user permissions are derived strictly from database queries on the verified user subject ID (`sub`), never from mutable client request headers.
3. **CORS & Origin Hardening**: Explicit origin whitelisting (`NEXT_PUBLIC_SITE_URL`, Vercel production domains). Wildcard `*` origins are blocked.
4. **Secret Scrubbing & Sentry Hygiene**: PII and credential scrubbing patterns sanitize passwords, tokens, API keys, and sensitive document text from observability pipelines.

---

## 6. Live Deployment & Infrastructure Endpoints

| Component | Provider | Live URL / Endpoint | Health Check Status |
|---|---|---|---|
| **Frontend** | Vercel (Next.js 14) | `https://knowflow-ai-pied.vercel.app` | **HTTP 200 OK** |
| **Backend API** | Render (FastAPI / Uvicorn) | `https://knowflow-ai-4ssd.onrender.com` | **HTTP 200 OK** |
| **Backend Health** | Render | `https://knowflow-ai-4ssd.onrender.com/api/health` | **HTTP 200 OK** (`healthy`) |
| **Backend Liveness** | Render | `https://knowflow-ai-4ssd.onrender.com/api/health/live` | **HTTP 200 OK** (`alive`) |
| **Backend Readiness**| Render | `https://knowflow-ai-4ssd.onrender.com/api/health/ready` | **HTTP 200 OK** (`ready: true`) |
| **Database & Auth** | Supabase (AWS ap-south-1) | `https://jlbpfgfafobynepeytyl.supabase.co` | **Connected & Verified** |

---

## 7. Environment Variables Reference

### Backend Configuration (`backend/.env`)

| Variable | Description | Required | Example / Default |
|---|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string with asyncpg driver | Yes | `postgresql+asyncpg://postgres:secret@host:5432/db` |
| `DIRECT_DATABASE_URL` | Direct PostgreSQL connection string for Alembic | Yes | `postgresql://postgres:secret@host:5432/db` |
| `ENVIRONMENT` | Runtime environment (`production`, `development`, `test`) | Yes | `production` |
| `CORS_ORIGINS` | Comma-separated list of allowed CORS origins | Yes | `https://knowflow-ai-pied.vercel.app` |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | Yes | `https://<project-ref>.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY`| Supabase anonymous API key | Yes | `<anon-jwt-key>` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase administrative service role key | Yes | `<service-role-key>` |
| `LLM_PROVIDER` | Language model provider (`groq`, `openai`, `gemini`) | Yes | `groq` |
| `GROQ_API_KEY` / `OPENAI_API_KEY`| API key for configured LLM provider | Yes | `<api-key>` |
| `EMBEDDING_PROVIDER` | Embedding model provider (`fastembed`, `openai`) | Yes | `fastembed` |
| `SENTRY_DSN` | Sentry error tracking DSN (optional) | No | `""` |

### Frontend Configuration (`frontend/.env.local`)

| Variable | Description | Required | Example |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | URL of the backend FastAPI service | Yes | `https://knowflow-ai-4ssd.onrender.com` |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | Yes | `https://<project-ref>.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY`| Supabase public anon key | Yes | `<anon-jwt-key>` |
| `NEXT_PUBLIC_SITE_URL` | Canonical frontend origin | Yes | `https://knowflow-ai-pied.vercel.app` |

---

## 8. Local Development & Setup Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- PostgreSQL 16 with pgvector extension (or Supabase local/cloud)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local

# Start Next.js development server
npm run dev -- -p 3000
```

---

## 9. Testing & Quality Assurance

KnowFlow AI maintains an automated regression suite and CI quality pipeline.

```bash
# Run full backend test suite (88 tests)
python -m pytest backend/tests -v

# Run OpenAPI drift verification test
python -m pytest backend/tests/test_openapi_contract_drift.py -v

# Run frontend type checking & build verification
cd frontend
npm run lint
npx tsc --noEmit
npm run build

# Run Live Cloud E2E verification harness
python -u scripts/test_phase6_cloud_e2e.py
```

---

## 10. Operational Limitations & Boundaries

To preserve strict technical integrity, the following limitations are explicitly documented:
1. **Rate Limiting Scope**: The current rate limiter operates on an in-memory sliding window per application process. In multi-worker or horizontally scaled cluster deployments, rate limiting requires a centralized store (e.g. Redis).
2. **Audit Log Immutability**: Audit logs are persisted in PostgreSQL relational tables. Cryptographic write-once or append-only immutability is not currently implemented.
3. **Continuous Deployment Reality**: Production deployments use provider-native Git triggers on Vercel and Render. GitHub Actions workflows enforce CI quality and security scans without automated provider deployment secrets.
4. **Sentry Error Transmission**: Sentry PII sanitization and handler fallbacks are unit-tested, but live transmission is unconfigured when `SENTRY_DSN` is omitted.
5. **External Uptime Monitoring**: Health and readiness probes are live, but third-party synthetic pingers (e.g. BetterStack) are not pre-configured.
6. **Recovery Metrics**: Database backup and restore duration is empirically measured at **28.08 seconds** (SHA-256 state parity verified across 16/16 tables). Total operational RTO is a modeled estimate of **12.47 minutes**; RPO continuous PITR $\le 5$ min is a cloud provider capability not empirically measured via deliberate data-loss recovery.

---

## 11. Interactive Demo Walkthrough

1. **Access**: Navigate to `https://knowflow-ai-pied.vercel.app/login`.
2. **Authenticate**: Log in with authorized credentials or provision a test user.
3. **Workspace**: View your isolated workspace dashboard and document repository.
4. **Document Ingestion**: Upload a PDF or TXT standard operating procedure (e.g. `sop_cleanroom.txt`).
5. **Grounded Query**: Ask *"What is the required temperature range for ISO 7 cleanrooms?"*
6. **Inspect Citations**: Review the citation cards showing exact document title, section heading, and verified text excerpt.
7. **Negative Test / Hallucination Refusal**: Ask an out-of-domain question (e.g., *"What is the capital of Atlantis?"*). Observe the strict grounded refusal.
8. **Document Deletion**: Hard delete the test document and observe immediate purge from database and vector index.
9. **Logout**: Terminate authenticated session.

---

## 12. Documentation Index

- [Architecture Guide](file:///docs/architecture.md) — Comprehensive system design, retrieval pipelines, and data models.
- [Deployment Runbook](file:///docs/deployment.md) — Step-by-step deployment guide for Vercel, Render, and Supabase.
- [Security & Compliance](file:///docs/security.md) — Detailed threat modeling, RBAC, tenant isolation, and secret management.
- [Operations & Monitoring](file:///docs/operations.md) — Health probes, database migrations, disaster recovery, and logging.
- [Troubleshooting Runbook](file:///docs/troubleshooting.md) — Diagnostic guide for common backend, frontend, and cloud issues.
- [API Reference](file:///docs/api.md) — OpenAPI 3.1 endpoint specifications and payload contracts.
- [Phase 6 Final Report](file:///docs/phase_6_final_report.md) — Final deployment verification evidence and certification sign-off.
- [Portfolio Case Study](file:///docs/portfolio_project.md) — Full-stack engineering case study and technical highlights.

---

## License

MIT License. Copyright (c) 2026 KnowFlow AI Contributors.
