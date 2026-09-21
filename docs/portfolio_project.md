# KnowFlow AI — Engineering Portfolio Project

## Project: KnowFlow AI — Enterprise RAG Knowledge Assistant

### Live Production Deployment
- **Frontend**: [https://knowflow-ai-pied.vercel.app](https://knowflow-ai-pied.vercel.app)
- **Backend API**: [https://knowflow-ai-4ssd.onrender.com](https://knowflow-ai-4ssd.onrender.com)
- **Repository**: [https://github.com/Abhitechdev/knowflow-ai](https://github.com/Abhitechdev/knowflow-ai)

---

## 1. Executive Summary & Problem Space

In enterprise environments, standard operating procedures (SOPs), safety compliance documents, and equipment manuals are locked in unstructured documents across siloed file systems. Standard conversational AI tools suffer from hallucination and lack fine-grained data isolation.

**KnowFlow AI** was built to solve these challenges with production-grade rigor:
- **Zero Hallucination Tolerance**: Employs a strict Grounded Answering Policy — refusing to fabricate facts when supporting documentation is absent.
- **Auditable Traceability**: Every generated assertion is mapped directly to exact source document sections, page numbers, and verified text excerpts.
- **Enterprise Security**: Implements fail-closed Supabase JWT authentication, server-enforced workspace tenant isolation, and granular Role-Based Access Control (RBAC).

---

## 2. Technical Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Lucide Icons |
| **Backend API** | Python 3.11, FastAPI, Pydantic v2, Async SQLAlchemy 2.0, Uvicorn |
| **Data & Vector Storage** | PostgreSQL 16 with `pgvector` (Supabase Cloud) |
| **Authentication & IAM** | Supabase Auth (GoTrue) — Bearer JWT with fail-closed production enforcement |
| **Retrieval Architecture**| Hybrid Retrieval (Dense pgvector + Sparse BM25) with Reciprocal Rank Fusion (RRF) |
| **Migrations & DB Ops** | Alembic versioned migrations, custom backup & disaster recovery verification |
| **Testing & CI/CD** | Pytest, Pytest-Asyncio (88 tests), GitHub Actions CI, Docker |

---

## 3. Architecture & Data Flow

```
Enterprise User
      │
      ▼
Next.js 14 Frontend (Vercel)
      │  HTTPS / Bearer JWT
      ▼
FastAPI Application Server (Render)
      │
      ├── 1. UserContext Guard (Fail-closed JWT & Workspace DB Lookup)
      ├── 2. Prompt Injection & Jailbreak Sanitizer
      ├── 3. Hybrid Retrieval Engine (pgvector Dense + BM25 Sparse)
      ├── 4. Reciprocal Rank Fusion (RRF k=60) & Hybrid Reranking
      ├── 5. RBAC Clearance Filter (PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED)
      ├── 6. Context-Constrained Grounded Synthesis (LLM)
      └── 7. Structured Response with Citations & Source Excerpts
            │
            ▼
PostgreSQL 16 + pgvector (Supabase Cloud)
```

---

## 4. Key Engineering Accomplishments

1. **Hybrid Retrieval with RRF**: Combined vector semantic similarity with BM25 lexical precision to resolve exact acronyms, technical IDs, and natural phrasing.
2. **Empirically Proven Disaster Recovery**: Verified database restore capability under Gate 5F-2 in **28.08 seconds** with 100% SHA-256 state parity across all 16 tables and pgvector 384-dim index integrity.
3. **Fail-Closed Multi-Tenant Security**: Enforced workspace and clearance boundary isolation at the database query layer. Verified unauthenticated 401 rejections and zero cross-tenant visibility in live cloud testing.
4. **Automated OpenAPI Contract Guard**: Continuous integration test comparing `docs/openapi.json` against `app.openapi()` across 34 endpoints and 26 schemas to guarantee zero frontend/backend drift.
5. **Comprehensive Automated Test Coverage**: 88/88 backend regression tests covering auth, RBAC, document chunking, embeddings, RAG generation, rate limiting, and hard deletion cascades.

---

## 5. Verified Engineering Benchmarks

> **Dataset Scope**: Curated 15-case engineering benchmark derived from realistic compliance and SOP document sets.

- **Hit@1**: **81.8%**
- **Hit@3**: **100.0%**
- **Hit@5**: **100.0%**
- **Mean Reciprocal Rank (MRR)**: **0.8939**
- **NDCG@5**: **0.9210**
- **Backend Test Suite**: **88 / 88 Passing (100%)**
