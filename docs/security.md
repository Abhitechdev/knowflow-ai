# KnowFlow AI — Security Architecture & Threat Model

## 1. Authentication & Session Management

KnowFlow AI utilizes Supabase Auth for cryptographically signed JWT tokens (RS256 / HS256).

### 1.1 Fail-Closed Security Policy
- When running in production (`ENVIRONMENT=production`), every protected route requires a valid Bearer JWT header.
- If the token is absent, expired, invalid, or malformed, the API immediately halts execution with `HTTP 401 Unauthorized`.
- Development fallback contexts are strictly disabled when `ENVIRONMENT=production`.

### 1.2 Server-Side Context & Identity Resolution
- The client cannot spoof identity or tenant parameters via headers or query parameters (e.g. `X-Workspace-Id` or `user_id`).
- The backend resolves the authenticated user subject ID (`sub`) directly from the verified JWT claims, then executes an internal database lookup to retrieve the authorized `WorkspaceMember` record, role, and department.

---

## 2. Multi-Tenant Isolation & Authorization (RBAC)

### 2.1 Workspace Isolation
- Every database query across `documents`, `document_chunks`, `conversations`, and `audit_logs` explicitly filters by `workspace_id == user_context.workspace_id`.
- Foreign workspace queries are rejected with `HTTP 403 Forbidden` or return empty filtered results.

### 2.2 Role-Based Document Clearance Levels
- Documents are tagged with an `access_level`:
  - `PUBLIC`: Accessible by all employees.
  - `INTERNAL`: Standard workspace access.
  - `CONFIDENTIAL`: Restricted to `MANAGER`, `COMPLIANCE_OFFICER`, and `ADMIN`.
  - `RESTRICTED`: Strictly restricted to `ADMIN`.
- Retrieval queries dynamically inject clearance filters before executing pgvector similarity searches.

---

## 3. RAG Security & Prompt Injection Defense

### 3.1 Prompt Injection Guardrails
- Inbound user queries pass through regex and heuristic pattern detectors targeting:
  - System prompt overrides (`"ignore previous instructions"`, `"you are now an unrestricted AI"`)
  - Delimiter escape sequences (`<SYSTEM>`, `[INSTRUCTION]`, `"""`)
  - Role manipulation and data exfiltration patterns.
- Detected injection attempts trigger an immediate rejection or sanitized containment response.

### 3.2 Grounded Answering Constraint
- System prompts strictly forbid the LLM from utilizing external pre-training knowledge when answering domain questions.
- If retrieved context does not contain sufficient factual evidence, the LLM is instructed to respond with the standard grounded refusal:
  > *"Under KnowFlow's Grounded Answering Policy, I can only provide answers verified by authorized company documentation."*

---

## 4. Data Privacy, Storage & Hard Deletion

### 4.1 Storage Security
- Supabase Storage buckets are configured as **Private**. Direct unauthenticated public downloads are disabled.
- File downloads are conducted server-side via authenticated service credentials or time-limited signed URLs.

### 4.2 Hard Deletion & Purging
- When a document is deleted via `DELETE /api/v1/documents/{document_id}`:
  1. Associated `document_chunks` and pgvector embeddings are deleted in the same database transaction.
  2. Document permission records are removed.
  3. The raw file blob is deleted from Supabase Storage.
  4. An audit log entry (`DOCUMENT_DELETED`) is recorded with sanitized metadata (excluding file contents).

---

## 5. Observability Hygiene & PII Scrubbing

- The logging and error reporting systems incorporate strict PII scrubbing.
- Fields matching `password`, `token`, `authorization`, `cookie`, `secret`, `api_key`, `query`, `content`, or `message` are automatically redacted (`[REDACTED]`) prior to transmission to logs or error trackers.
- Secret credentials (`DATABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `JWT_SECRET`, API keys) are never exposed in health checks, API responses, or repository commits.
