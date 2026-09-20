# KnowFlow AI — Portfolio Case Study

> **Target roles**: Associate AI Engineer · Junior Full-Stack Engineer · AI/ML Developer (Entry-Level / Early-Career)

---

## Project Summary

**KnowFlow AI** is a full-stack, enterprise-grade RAG (Retrieval-Augmented Generation) document intelligence platform built from scratch. It enables organizations to query internal company SOPs and policy documents using natural language — and receive grounded, citation-backed answers that refuse to fabricate information outside the authorized document corpus.

The project demonstrates end-to-end software engineering: from building a hybrid dense+sparse search pipeline and LLM grounding policy, to containerized deployment, automated evaluation, and production hardening.

**Key stats:**
- **68 automated tests** — all passing
- **NDCG@5 = 0.9210, MRR = 0.8939** on a 15-case curated benchmark *(benchmark result, not universal claim)*
- **0 false positives, 0 false negatives** in grounding evaluation on benchmark dataset
- **33 REST API endpoints** with OpenAPI 3.1 specification
- Full production hardening: fail-closed auth, RBAC, security headers, rate limiting, audit logging

---

## Technical Architecture

### Core RAG Pipeline

```
Document Upload
    → Text Extraction (TXT, PDF, DOCX, MD)
    → Semantic Chunking (configurable overlap + size)
    → Dual Embedding: Dense (OpenAI) + Sparse (BM25)
    → Hybrid Retrieval (RRF fusion)
    → HybridReranker (BM25 + semantic score fusion, heuristic)
    → Prompt Injection Guardrails
    → Grounded Answering Policy (citation-required, refuses when unsupported)
    → Structured Response with Citations
```

### Key Design Decision: HybridReranker

I implemented a **heuristic HybridReranker** (not a neural cross-encoder) that combines BM25 keyword scores with dense embedding similarity using configurable weights. This choice was deliberate:

- **Cross-encoders** (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`) achieve slightly higher NDCG in offline benchmarks but add ~200-400ms latency and significant memory overhead per query.
- **For a document-scoped enterprise RAG** system where the corpus is curated and controlled, the latency/accuracy trade-off clearly favors a heuristic reranker at this scale.

This is a real engineering trade-off, not a compromise — and it's documented so a future engineer could swap in a cross-encoder when query volume justifies it.

### Grounded Answering Policy

The system enforces a strict grounding policy:
- If retrieved chunks do not support the query, the system **refuses with an explanation** — it never generates an answer from general LLM knowledge.
- This is enforced at the prompt level AND verified by a faithfulness evaluator.
- On the curated benchmark: **0 false positives** (no hallucinated answers accepted as grounded).

---

## Evaluation Framework

The 15-case golden benchmark tests:
1. **In-scope known-answer queries** — verified answer matches source document facts.
2. **Semantic paraphrase queries** — verifies retrieval generalizes beyond exact keyword matching.
3. **Out-of-scope queries** — verifies the system refuses rather than fabricating answers.
4. **Deviation/escalation queries** — verifies correct SOP step retrieval.

Metrics (curated benchmark results):
| Metric | Value | Description |
|--------|-------|-------------|
| NDCG@5 | 0.9210 | Ranking quality (normalized to [0, 1]) |
| MRR | 0.8939 | Mean Reciprocal Rank |
| False Positives | 0 | Hallucinated answers accepted as grounded |
| False Negatives | 0 | Grounded answers incorrectly refused |
| Pass Rate | 15/15 | All benchmark cases pass |

> **Note**: These metrics reflect performance on a controlled 15-case benchmark curated from the demo document set. They are engineering validation results, not general open-domain performance claims.

---

## Production Hardening Implemented

| Feature | Implementation |
|---------|---------------|
| Authentication | Supabase JWT — fail-closed in production (HTTP 401 when missing/invalid) |
| Authorization | Role-based access: ADMIN > MANAGER > EMPLOYEE with document clearance levels |
| Admin RBAC | `require_admin` dependency on all admin endpoints (HTTP 403 for non-admin) |
| Security Headers | HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy |
| CORS | Explicit origin allowlist — no wildcards |
| Rate Limiting | Sliding window rate limiter on chat endpoint |
| Audit Logging | Every query logged with user ID, workspace, timestamp |
| Prompt Injection | Pattern-based injection guardrails on all user input |
| Error Handling | Structured RFC 7807 error responses; Sentry integration (production) |
| Observability | `/health/live` (liveness) + `/health/ready` (deep readiness probe) |
| CI/CD | GitHub Actions: lint, test, secret detection (gitleaks), trivy container scan |

---

## Technologies Used

**Backend:** Python 3.11, FastAPI, SQLAlchemy (async), Alembic, pgvector, OpenAI API, FastEmbed

**Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Supabase Auth

**Infrastructure:** Docker (python:3.11-slim), Docker Compose, optional Nginx, GitHub Actions

**Database:** PostgreSQL with pgvector extension (Supabase managed)

**Testing:** Pytest (68 tests), Starlette TestClient

---

## Engineering Highlights for Resume

- Built a **hybrid RAG retrieval pipeline** combining dense embeddings (OpenAI) with BM25 sparse retrieval using Reciprocal Rank Fusion — achieving NDCG@5 = 0.9210 on a curated 15-case benchmark.
- Implemented a **Grounded Answering Policy** that enforces citation requirements and refuses out-of-scope queries — verified with 0 false positives on the benchmark.
- Developed a **production-hardened FastAPI backend** with fail-closed JWT authentication, role-based access control, sliding-window rate limiting, prompt injection guardrails, and structured audit logging.
- Achieved **68/68 automated tests passing** across unit, integration, and evaluation test suites.
- Containerized the full stack using **Docker (python:3.11-slim)** with configurable Uvicorn workers and optional Nginx reverse proxy, with a complete GitHub Actions CI/CD pipeline including secret detection (gitleaks) and container vulnerability scanning (trivy).

---

## Challenges & Learning

### Challenge 1: Grounding without hallucination
The hardest problem was making the LLM refuse gracefully rather than confidently hallucinating. The solution was a two-layer defense: a strict grounding prompt that provides only retrieved chunks as context, combined with a faithfulness evaluator that checks whether the answer is actually supported by the retrieved content.

### Challenge 2: Accurate NDCG normalization
During Phase 4, a reported NDCG value was found to be unnormalized (not bounded in [0, 1]). Investigated, fixed the normalization formula, and added a unit test confirming the metric stays in [0, 1] across all benchmark cases. This kind of metric validation discipline is essential in ML engineering.

### Challenge 3: Authentication fail-closed vs. developer experience
Balancing a strict production security requirement (fail-closed auth) with the need for a usable development environment. Solved with an `allow_test_auth_bypass` property gated strictly by `ENVIRONMENT != production`, with clear logging whenever the bypass is active.

---

## Source Code

**Repository:** [github.com/yourusername/knowflow-ai](https://github.com/yourusername/knowflow-ai)  
*(Update with actual repository link before sharing)*
