# KnowFlow AI — Architecture & Design Specification

## System Architecture

```
                                  +-----------------------+
                                  |     Web Browser       |
                                  |  Next.js 14 App Router|
                                  +-----------+-----------+
                                              | HTTPS / JSON
                                              v
                                  +-----------------------+
                                  |     FastAPI Core      |
                                  |   (Domain Services)   |
                                  +-----------+-----------+
                                              |
                     +------------------------+------------------------+
                     |                        |                        |
                     v                        v                        v
          +--------------------+    +--------------------+    +--------------------+
          |   Auth Interface   |    | Database Layer     |    | Storage Interface  |
          | (Supabase Adapter) |    | (SQLAlchemy Async) |    | (Supabase Storage) |
          +--------------------+    +---------+----------+    +--------------------+
                                              |
                                              v
                                    +--------------------+
                                    | PostgreSQL 16 +    |
                                    | pgvector           |
                                    +--------------------+
```

## Domain Entity Model

```
+-----------------------------------------------------------------------------------+
|                                     Workspaces                                    |
|  - id, name, slug                                                                 |
+--------+----------------------------+-----------------------------+---------------+
         | 1:N                        | 1:N                         | 1:N
         v                            v                             v
+-------------------+        +--------------------+        +--------------------+
|    Departments    |        |  WorkspaceMembers  |        |     Documents      |
|  - id, name       |        |  - user_id, role   |        |  - title, status   |
+-------------------+        +--------------------+        |  - access_level    |
                                                           +---------+----------+
                                                                     | 1:N
                                                                     v
                                                           +--------------------+
                                                           |  DocumentChunks    |
                                                           |  - page, section   |
                                                           |  - content, vector |
                                                           +--------------------+

+-----------------------------------------------------------------------------------+
|                                 Conversations & RAG                               |
+-----------------------------------------------------------------------------------+
|  Conversations (id, user_id, workspace_id, title)                                 |
|       | 1:N                                                                       |
|  Messages (id, sender_type: USER | ASSISTANT | SYSTEM, content)                   |
|       | 1:N                                                                       |
|  MessageSources (document_id, chunk_id, page_number, section_heading, text)       |
+-----------------------------------------------------------------------------------+

+-----------------------------------------------------------------------------------+
|                           Governance & Quality Assurance                          |
+-----------------------------------------------------------------------------------+
|  Feedback (message_id, rating, category, comments)                                |
|  AuditLogs (workspace_id, user_id, action, metadata_json, created_at)             |
|  UsageEvents (workspace_id, user_id, event_type, tokens, latency_ms)              |
|  EvaluationDatasets -> EvaluationQuestions -> EvaluationRuns                      |
+-----------------------------------------------------------------------------------+
```

## Phase 1 Status: Foundation Verified
- Monorepo structure established.
- FastAPI backend starts natively on Windows without requiring Docker.
- Database connection abstraction gracefully handles unconfigured local states while targeting PostgreSQL + pgvector.
- Full domain schema mapped in SQLAlchemy declarative models.
- Unit and integration tests passing (`pytest`).
- Next.js frontend connecting to `/api/health`.
