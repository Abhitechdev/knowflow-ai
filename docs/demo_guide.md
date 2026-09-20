# KnowFlow AI — Live Demo Guide

A step-by-step walkthrough for demonstrating KnowFlow AI to stakeholders or during technical interviews.

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.11+ |
| Node.js | 20+ |
| PostgreSQL with pgvector | 16+ |
| OpenAI API key | — |

---

## Quick Start (Local)

```bash
# 1. Clone and set up
git clone https://github.com/yourusername/knowflow-ai
cd knowflow-ai
cp .env.example .env  # Fill in your OpenAI key and Supabase credentials

# 2. Start backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 3. Start frontend (new terminal)
cd frontend
npm install
npm run dev

# 4. Open http://localhost:3000
```

---

## Demo Scenario Flow (10-minute walkthrough)

### Scene 1: Document Ingestion (2 min)
1. Navigate to **Admin Dashboard** → **Documents**.
2. Upload `Cold-Chain-SOP.txt` from `/demo_documents/`.
3. Show the ingestion pipeline: text extraction → chunking → embedding → indexing.
4. Point out the document metadata (access level, department, workspace).

**Talking point**: *"Every document gets dual-indexed — dense embeddings for semantic similarity and BM25 for keyword matching. This is what enables hybrid retrieval."*

### Scene 2: Known-Answer RAG Query (2 min)
1. Navigate to **/chat**.
2. Ask: `What temperature range is required for cold chain storage?`
3. Show the response — point out:
   - The grounded answer citing specific temperatures.
   - The **citation card** showing document name, section, and supporting excerpt.
4. Ask: `How should temperature-sensitive materials be stored?` (semantic paraphrase)
5. Show that hybrid retrieval finds the relevant content despite different wording.

**Talking point**: *"The HybridReranker fuses BM25 keyword scores with dense similarity using Reciprocal Rank Fusion — so both exact keyword matches and semantic paraphrases score well."*

### Scene 3: Grounding Policy Refusal (1.5 min)
1. Ask: `Who won the 2022 FIFA World Cup?`
2. Show the system refusing — it does not answer from general knowledge.
3. Ask: `Tell me about our product pricing strategy.` (not in any uploaded document)
4. Show another refusal.

**Talking point**: *"The Grounded Answering Policy enforces that every answer must be supported by retrieved document chunks. On our 15-case benchmark, we achieved zero false positives — the system never accepted a hallucinated answer as grounded."*

### Scene 4: Admin Dashboard & Audit Logs (2 min)
1. Navigate to **Admin → Stats**.
2. Show: total documents, chunks, conversations, feedback counts.
3. Navigate to **Admin → Audit Logs**.
4. Show the audit trail: every query logged with user, timestamp, and workspace.

**Talking point**: *"Every query is logged in a tamper-evident audit trail. This provides auditability foundations relevant to regulated environments like pharma, finance, or healthcare."*

### Scene 5: Search Interface (1 min)
1. Navigate to **/search**.
2. Search: `temperature deviation protocol`
3. Show ranked results with relevance scores and document excerpts.

### Scene 6: Health & Observability (1 min)
Open in browser:
- `http://localhost:8000/api/health/live` — liveness probe
- `http://localhost:8000/api/health/ready` — deep readiness (checks DB, auth, app)

**Talking point**: *"The readiness probe checks the full dependency stack — database connectivity, pgvector extension, and auth provider configuration. Orchestrators use this for traffic routing decisions."*

### Scene 7: Test Suite (30 sec)
```bash
pytest backend/tests -v --tb=short
# 68 passed
```
**Talking point**: *"68 automated tests covering unit, integration, evaluation, RBAC, prompt injection, rate limiting, and resilience. All tests pass."*

---

## Common Interview Questions & Answers

**Q: Why not use a vector DB like Pinecone or Weaviate?**
> We use pgvector with PostgreSQL. It collocates structured metadata (workspace, user, access level) with vector data in the same database — avoiding distributed query complexity for a system at this scale. pgvector supports IVFFlat and HNSW indexes and is fully managed by Supabase.

**Q: Why a heuristic HybridReranker instead of a cross-encoder?**
> Cross-encoders like `cross-encoder/ms-marco-MiniLM-L-6-v2` add 200–400ms latency and significant memory per query. For a controlled enterprise document corpus where precision on the top-5 results matters more than recall across millions of documents, the heuristic reranker achieves competitive accuracy at much lower operational cost. It's a deliberate engineering trade-off, not a capability gap.

**Q: How do you prevent hallucination?**
> Two-layer defense: (1) the system prompt includes only retrieved document chunks — the LLM cannot access general knowledge; (2) a faithfulness evaluator checks whether the answer is supported by the retrieved content. On our benchmark, zero false positives (hallucinated answers accepted as grounded).

**Q: How would you scale this for 10,000 users?**
> Horizontal scaling of Uvicorn workers (configurable via `WEB_CONCURRENCY`), Supabase connection pooler (PgBouncer at port 6543), async SQLAlchemy for I/O-bound operations, and Redis-backed rate limiting. The embedding and LLM calls are the main bottleneck — those would move to a dedicated async worker queue (Celery/Inngest) for high-volume ingestion.

---

## Files Reference

| File | Purpose |
|------|---------|
| `backend/app/rag/retrieval.py` | Hybrid retrieval + HybridReranker |
| `backend/app/rag/base.py` | Grounded Answering Policy |
| `backend/app/auth/context.py` | Fail-closed auth + require_admin |
| `backend/app/evaluation/engine.py` | RAG evaluation engine |
| `backend/app/evaluation/metrics.py` | NDCG@K, MRR, precision metrics |
| `scripts/production_smoke_test.py` | Staging-first smoke test harness |
| `.github/workflows/ci-cd.yml` | Full CI/CD pipeline |
| `docs/disaster_recovery.md` | Backup and restore runbook |
