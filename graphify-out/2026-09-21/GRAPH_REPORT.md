# Graph Report - ragproject  (2026-09-21)

## Corpus Check
- 206 files · ~121,805 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: .example 5, (none) 4, .woff 2)

## Summary
- 1768 nodes · 2943 edges · 151 communities (112 shown, 39 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 150 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b5a4bbec`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- endpoints/chat.py
- engine.py
- verify_phase5_local.py
- ResilientLLMInvoker
- test_workspaces.py
- documents.py
- 2. Detailed Cloud Verification Evidence
- pydantic
- button.tsx
- test_production_auth.py
- SecurityHeadersMiddleware
- main.py
- RankedChunk
- rate_limiter.py
- run_gate_5e_cloud_suite.py
- compilerOptions
- production_smoke_test.py
- PromptInjectionGuard
- retrieval.py
- chat/page.tsx
- lucide-react
- test_reranker.py
- layout.tsx
- SupabaseStorageService
- package.json
- llm.py
- dependencies
- cn
- brandkit/SKILL.md
- backup_db.py
- CORE DIRECTIVE: IMAGE-FIRST WEBSITE DESIGN TO CODE
- test_admin.py
- UserContext
- api.ts
- embeddings/__init__.py
- supabase/middleware.ts
- test_gate_5e_full_cloud.py
- CORE DIRECTIVE: PREMIUM MOBILE APP IMAGE DIRECTION
- test_restore.py
- High-Agency Frontend Skill
- ContextBudgetManager
- audit_security.py
- Appendix B - Canonical Sources (read these before reinventing)
- session.py
- extends
- Design Audit
- next.config.mjs
- postcss.config.mjs
- Analysis & Synthesis Instructions
- Agent Skill: Principal UI/UX Architect & Motion Choreographer (Awwwards-Tier)
- Supabase
- CORE DIRECTIVE: AWWWARDS-LEVEL IMAGE ART DIRECTION
- SKILL: Industrial Brutalism & Tactical Telemetry UI
- Changelog
- Changelog
- Writing Guidelines for Postgres References
- Settings
- Design System: Taste Standard
- 2. THE COMBINATORIAL VARIATION ENGINE
- export_openapi.py
- KnowFlow AI — Enterprise Knowledge & SOP Agent
- 4. DESIGN ENGINEERING DIRECTIVES (Bias Correction)
- endpoints/health.py
- KnowFlow AI — Portfolio Case Study
- 10. REFERENCE VOCABULARY (Pattern Names the Agent Should Know)
- tasteskill: Anti-Slop Frontend Skill
- CORE DIRECTIVE: AWWWARDS-LEVEL DESIGN ENGINEERING
- 22. STYLE VARIATION ENGINE
- Protocol: Premium Utilitarian Minimalism UI Architect
- Section Definitions
- 11. COMPONENT EXECUTION GUIDELINES
- 18. EXTRA CREATIVITY & IMPLEMENTATION EDGE
- Ponytail
- context.py
- make_settings
- 9. AI TELLS (Forbidden Patterns)
- 12. THE COMBINATORIAL VARIATION ENGINE
- 8. ANTI-AI-SLOP RULES
- Ponytail Help
- devDependencies
- 11. REDESIGN PROTOCOL
- 3. DEFAULT ARCHITECTURE & CONVENTIONS
- 6. PERFORMANCE & ACCESSIBILITY GUARDRAILS
- Full-Output Enforcement
- 33. CATEGORY-SPECIFIC BIAS
- 13. COLOR & MATERIAL RULES
- 4. HERO MINIMALISM RULES
- require_admin
- 29. ANTI-AI-SLOP RULES
- 5. IMAGE COUNT & PAGE SLICING
- Supabase Postgres Best Practices
- time
- 0. BRIEF INFERENCE (Read the Room Before Anything Else)
- 12. THE BLOCK LIBRARY (Contract - Implementations Land Here Iteratively)
- 5. CONTEXT-AWARE PROACTIVITY
- 8. DARK MODE PROTOCOL
- 21. MOBILE ANTI-AI-TELLS RULE
- ponytail-audit/SKILL.md
- Ponytail Gain
- ponytail-review/SKILL.md
- logging
- CLINICAL OPERATIONS SOP: REFRIGERATED STORAGE & COLD CHAIN INTEGRITY
- Challenges & Learning
- 7. DIAL DEFINITIONS (Technical Reference)
- 33. DEFAULT SECTION PACKS
- 14. HERO MINIMALISM RULES
- 37. EXAMPLE INTERPRETATIONS
- 2. PLATFORM MODE RULE
- 37. EXAMPLE INTERPRETATIONS
- 15. DEFAULT SITE PACKS
- 20. EXAMPLE INTERPRETATIONS
- ponytail-debt/SKILL.md
- sentry.py
- frontend/README.md
- backend-status-indicator.tsx
- rules/graphify.md
- advanced-full-text-search.md
- advanced-jsonb-indexing.md
- conn-idle-timeout.md
- conn-limits.md
- conn-pooling.md
- conn-prepared-statements.md
- data-batch-inserts.md
- data-n-plus-one.md
- data-pagination.md
- data-upsert.md
- lock-advisory.md
- lock-deadlock-prevention.md
- lock-short-transactions.md
- lock-skip-locked.md
- monitor-explain-analyze.md
- monitor-pg-stat-statements.md
- monitor-vacuum-analyze.md
- query-composite-indexes.md
- query-covering-indexes.md
- query-index-types.md
- query-missing-indexes.md
- query-partial-indexes.md
- schema-constraints.md
- schema-data-types.md
- schema-foreign-key-indexes.md
- schema-lowercase-identifiers.md
- schema-partitioning.md
- schema-primary-keys.md
- security-privileges.md
- security-rls-basics.md
- security-rls-performance.md
- _template.md
- workflows/graphify.md

## God Nodes (most connected - your core abstractions)
1. `UserContext` - 52 edges
2. `CORE DIRECTIVE: IMAGE-FIRST WEBSITE DESIGN TO CODE` - 39 edges
3. `CORE DIRECTIVE: PREMIUM MOBILE APP IMAGE DIRECTION` - 39 edges
4. `RankedChunk` - 36 edges
5. `Base` - 33 edges
6. `HybridRetriever` - 26 edges
7. `CORE DIRECTIVE: AWWWARDS-LEVEL IMAGE ART DIRECTION` - 22 edges
8. `lucide-react` - 20 edges
9. `react` - 20 edges
10. `get_current_user_context()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `Production Hardening Implemented` --references--> `require_admin()`  [INFERRED]
  docs/portfolio_case_study.md → backend/app/auth/context.py
- `main()` --uses--> `UserContext`  [INFERRED]
  scripts/check_retrieval.py → backend/app/auth/context.py
- `run_e2e_smoke_tests()` --uses--> `UserContext`  [INFERRED]
  scripts/e2e_manual_smoke_test.py → backend/app/auth/context.py
- `ensure_unauth_fixtures()` --calls--> `get_session_factory()`  [INFERRED]
  scripts/e2e_manual_smoke_test.py → backend/app/db/session.py
- `main()` --calls--> `get_session_factory()`  [INFERRED]
  scripts/verify_phase4_evaluation.py → backend/app/db/session.py

## Import Cycles
- None detected.

## Communities (151 total, 39 thin omitted)

### Community 0 - "endpoints/chat.py"
Cohesion: 0.07
Nodes (65): app_db_base, app_schemas_chat, AdminStatsResponse, AuditLogItem, get_admin_stats(), get_audit_logs(), AsyncSession, BaseModel (+57 more)

### Community 1 - "engine.py"
Cohesion: 0.08
Nodes (41): BenchmarkCase, BaseModel, Curated Golden Benchmark Dataset for KnowFlow AI RAG Evaluation. Contains…, CaseEvaluationResult, EvaluationEngine, EvaluationSummary, AsyncSession, BaseModel (+33 more)

### Community 2 - "verify_phase5_local.py"
Cohesion: 0.17
Nodes (24): get_latest_evaluation_summary(), Returns the most recent automated evaluation summary., liveness_probe(), Lightweight process liveness check. Returns 200 OK as long as the process is…, hybrid_search(), AsyncSession, Executes hybrid (dense vector + sparse BM25) search across authorized company…, BaseModel (+16 more)

### Community 3 - "ResilientLLMInvoker"
Cohesion: 0.11
Nodes (18): CircuitBreakerOpenException, Production LLM Resilience Engine for KnowFlow AI. Enforces: 1. Per-request…, Raised when circuit breaker is tripped open to fail fast., Wraps LLM invocations with retry, secondary provider fallback, and circuit…, Returns True if the circuit breaker is currently tripped open., Executes LLM generation with retry -> secondary provider -> safe structured…, ResilientLLMInvoker, MockFailingProvider (+10 more)

### Community 4 - "test_workspaces.py"
Cohesion: 0.14
Nodes (28): app_api_v1_endpoints_workspaces, app_schemas_workspace, create_workspace(), AsyncSession, Creates a new workspace and sets the calling user as the ADMIN., AuthUser, BaseModel, get_auth_user_only() (+20 more)

### Community 5 - "documents.py"
Cohesion: 0.05
Nodes (53): app_schemas_document, delete_document(), get_document(), list_documents(), AsyncSession, delete, Lists real ingested documents from the database with pagination, filters, and…, Returns detailed information for a document, including extracted chunks and… (+45 more)

### Community 6 - "2. Detailed Cloud Verification Evidence"
Cohesion: 0.09
Nodes (21): 1. Executive Summary & Gate Status, 2. Detailed Cloud Verification Evidence, 3. Compliance & Factual Documentation Review, A. Deployment Identity & Version, B. Supabase Auth URL & Redirect Configuration, C. Real User Registration & Real SMTP Email Confirmation Flow, D. Session Persistence & Protected Route Access, E. Workspace Onboarding & Admin Assignment (+13 more)

### Community 7 - "pydantic"
Cohesion: 0.18
Nodes (9): PipelineTimings, BaseModel, Token Budgeting, Context Window Optimization & Latency Telemetry. Manages…, InjectionDetectionResult, BaseModel, Prompt Injection, Delimiter Sanitization & Input Guardrails. Defends KnowFlow…, Security, RBAC, and Guardrails module for KnowFlow AI., pydantic (+1 more)

### Community 8 - "button.tsx"
Cohesion: 0.27
Nodes (8): SearchPage(), Button, ButtonProps, buttonVariants, performHybridSearch(), SearchChunkResult, class-variance-authority, @radix-ui/react-slot

### Community 9 - "test_production_auth.py"
Cohesion: 0.33
Nodes (3): Tests for production authentication hardening and admin RBAC. Gate 5B…, TestSecurityHeadersMiddleware, unittest_mock

### Community 10 - "SecurityHeadersMiddleware"
Cohesion: 0.18
Nodes (9): Request, Security headers middleware for production hardening. Adds HSTS, CSP, X-Frame-…, Inject security response headers into every HTTP response. Headers applied: -…, SecurityHeadersMiddleware, BaseHTTPMiddleware, Response, starlette_middleware_base, starlette_requests (+1 more)

### Community 11 - "main.py"
Cohesion: 0.15
Nodes (11): app_api_router, app_core_security_headers, app_core_sentry, asyncio, root(), client(), fixture, setup_test_db() (+3 more)

### Community 12 - "RankedChunk"
Cohesion: 0.21
Nodes (12): RankedChunk, BaseReranker, HybridReranker, NoOpReranker, Stage 2 Reranking for KnowFlow AI. Implements HybridReranker, combining stage 1…, Abstract interface for Stage 2 rerankers., Pass-through reranker returning top_k chunks without modification., Calibrated two-stage HybridReranker. Combines stage 1 RRF scores with fine-… (+4 more)

### Community 13 - "rate_limiter.py"
Cohesion: 0.14
Nodes (16): _get_client_key(), Request, rate_limit_admin(), rate_limit_chat(), rate_limit_search(), Sliding-Window Rate Limiting & Abuse Protection. Tracks requests per IP and per…, In-memory sliding window rate limiter., Checks if a request under 'key' is allowed. Returns: (is_allowed,… (+8 more)

### Community 14 - "run_gate_5e_cloud_suite.py"
Cohesion: 0.19
Nodes (18): check_a_deployment_identity(), check_b_supabase_auth_config(), check_c_registration_flow(), handle_req(), check_d_session_cloud(), check_e_workspace_onboarding(), check_f_tenant_isolation(), check_g_document_rag_flow() (+10 more)

### Community 16 - "compilerOptions"
Cohesion: 0.11
Nodes (17): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+9 more)

### Community 17 - "production_smoke_test.py"
Cohesion: 0.28
Nodes (17): check(), confirm_production_target(), http_get(), http_post(), main(), Any, Production/Staging smoke test harness for KnowFlow AI. Targets STAGING by…, test_known_answer_rag() (+9 more)

### Community 18 - "PromptInjectionGuard"
Cohesion: 0.09
Nodes (9): PromptInjectionGuard, Multi-layer input sanitization and prompt injection defense., Strips non-printable control characters, zero-width characters, and neutralizes…, Inspects query text against known injection patterns and returns threat status., Wraps retrieved chunk text inside strict XML boundary tags with explicit…, Returns True if output does NOT contain the canary token (safe). Returns False…, guard(), fixture (+1 more)

### Community 19 - "retrieval.py"
Cohesion: 0.10
Nodes (24): compute_bm25_score(), cosine_similarity(), AsyncSession, Constructs server-side authorization SQL expressions. Never trust client-…, Executes hybrid retrieval enforcing server-side authorization., Tokenize and normalize text into lowercase terms., Computes standard BM25 score for a document given query terms., Calculates cosine similarity between two float vectors. (+16 more)

### Community 20 - "chat/page.tsx"
Cohesion: 0.16
Nodes (15): ChatContent(), HistoryPage(), getGreeting(), HomePage(), Input, InputProps, ChatMessage, ConversationDetail (+7 more)

### Community 21 - "lucide-react"
Cohesion: 0.16
Nodes (14): LoginPage(), OnboardingPage(), RegisterPage(), ResetPasswordPage(), SettingsPage(), UpdatePasswordPage(), AppShell(), NAV_ITEMS (+6 more)

### Community 22 - "test_reranker.py"
Cohesion: 0.19
Nodes (10): MessageContext, BaseModel, QueryRewriter, Query Rewriter & Multi-Turn Conversational Expander. Disambiguates…, Expands domain terminology and resolves multi-turn conversational references., Expands common domain acronyms while preserving original tokens., Rewrites elliptical/pronoun-heavy queries using prior conversation context., Unit tests for Stage 2 HybridReranker and QueryRewriter. (+2 more)

### Community 23 - "layout.tsx"
Cohesion: 0.29
Nodes (5): frontend_src_app_globals, inter, metadata, ToastProvider(), sonner

### Community 24 - "SupabaseStorageService"
Cohesion: 0.19
Nodes (7): Any, Service to interact directly with private Supabase Storage buckets via REST API., Uploads a file to the configured private Supabase Storage bucket., Downloads file bytes from private Supabase Storage., Deletes a file from Supabase Storage., Generates a secure temporary signed URL to download or view a private file., SupabaseStorageService

### Community 25 - "package.json"
Cohesion: 0.08
Nodes (22): name, private, scripts, build, dev, lint, start, version (+14 more)

### Community 26 - "llm.py"
Cohesion: 0.14
Nodes (22): CitationItem, GroundingAssessment, BaseModel, RAGResponse, RetrievalResult, GroundingEvaluator, Enforces the Grounded Answering Policy. The system must answer strictly from…, Determines whether the retrieved chunks provide sufficient, credible evidence… (+14 more)

### Community 27 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-slot, react (+5 more)

### Community 28 - "cn"
Cohesion: 0.35
Nodes (8): DialogContent, DialogDescription, DialogFooter(), DialogHeader(), DialogOverlay, DialogTitle, Skeleton(), cn()

### Community 29 - "brandkit/SKILL.md"
Cohesion: 0.05
Nodes (43): 1. Logo Cover, 1. Monogram + Meaning, 2 × 3 REFERENCE-STYLE LAYOUT, 2. Logo Construction, 2. Product Action, 3. Digital Application, 3. Metaphor Fusion, 4. Brand Essence (+35 more)

### Community 30 - "backup_db.py"
Cohesion: 0.20
Nodes (13): gzip, pathlib, get_db_url(), main(), parse_db_url(), Path, Verify backup file contains expected SQL content., Database backup script for KnowFlow AI. Creates a timestamped pg_dump snapshot… (+5 more)

### Community 31 - "CORE DIRECTIVE: IMAGE-FIRST WEBSITE DESIGN TO CODE"
Cohesion: 0.06
Nodes (34): 10. IMAGE-FIRST CODEX WEBSITE WORKFLOW, 11. WHEN TO TRIGGER IMAGE GENERATION FIRST, 13. WEBSITE REFERENCE RULE, 15. RESPONSIVE FIRST-VIEW RULE, 16. ANTI-NESTED-BOX RULE, 17. REDUCE MICRO-UI CLUTTER RULE, 18. SECTION IMAGE GENERATION RULE, 19. WEBSITE IMAGE SYSTEM RULE (+26 more)

### Community 32 - "test_admin.py"
Cohesion: 0.21
Nodes (10): TestClient, test_admin_audit_logs_endpoint(), test_admin_stats_endpoint(), test_evaluation_summary_endpoint(), TestClient, Verifies that asking a question creates Conversation, Message, and persists…, Verifies direct hybrid search endpoint., test_chat_query_and_persistence() (+2 more)

### Community 33 - "UserContext"
Cohesion: 0.20
Nodes (8): BaseModel, Returns list of document access levels this user is authorized to read., UserContext, TestUserContextAccessLevels, Unit tests for Phase 4 Granular RBAC and Document Clearance Hardening., test_hybrid_retriever_auth_filter_construction(), test_user_context_allowed_access_levels(), test_tenant_isolation_in_retriever()

### Community 34 - "api.ts"
Cohesion: 0.14
Nodes (25): AdminPage(), handleFilterAudit(), handleRunEvaluation(), loadInitialData(), DocumentsPage(), AdminStats, APIError, AuditLogRecord (+17 more)

### Community 35 - "embeddings/__init__.py"
Cohesion: 0.10
Nodes (15): BaseEmbeddingProvider, ABC, Returns the embedding vector dimension., Generates embeddings for a list of text chunks., Generates an embedding for a search query string., Abstract base class for embedding providers., get_embedding_provider(), Returns the singleton embedding provider based on application configuration. (+7 more)

### Community 36 - "supabase/middleware.ts"
Cohesion: 0.25
Nodes (7): GET(), IMPORTANT: Avoid writing any logic between createServerClient and, updateSession(), createClient(), config, middleware(), @supabase/ssr

### Community 37 - "test_gate_5e_full_cloud.py"
Cohesion: 0.36
Nodes (8): log_result(), test_deployment_identity(), test_e2e_browser_flows(), test_password_reset_flow(), test_rag_and_security_flows(), test_security_and_network(), test_supabase_auth_config(), test_tenant_isolation_and_rbac()

### Community 38 - "CORE DIRECTIVE: PREMIUM MOBILE APP IMAGE DIRECTION"
Cohesion: 0.06
Nodes (34): 10. DEVICE MOCKUP FRAME RULE, 11. ONBOARDING FLOW RULE, 12. FIRST SCREEN CLEANLINESS RULE, 13. SAFE AREA AND SYSTEM REGION RULE, 14. NAVIGATION RULE, 15. CLEAN LAYOUT RULE, 16. CREATIVE IMAGE DIRECTION RULE, 17. BACKGROUND TEXTURE AND SURFACE RULE (+26 more)

### Community 39 - "test_restore.py"
Cohesion: 0.24
Nodes (9): CompletedProcess, main(), parse_db_url(), Database restore verification test for KnowFlow AI. Performs an actual backup →…, Run a subprocess command and return the result., Parse a postgresql:// URL into components., run_cmd(), subprocess (+1 more)

### Community 40 - "High-Agency Frontend Skill"
Cohesion: 0.06
Nodes (30): 10. FINAL PRE-FLIGHT CHECK, 1. ACTIVE BASELINE CONFIGURATION, 2. DEFAULT ARCHITECTURE & CONVENTIONS, 3. DESIGN ENGINEERING DIRECTIVES (Bias Correction), 4. CREATIVE PROACTIVITY (Anti-Slop Implementation), 5. PERFORMANCE GUARDRAILS, 6. TECHNICAL REFERENCE (Dial Definitions), 7. AI TELLS (Forbidden Patterns) (+22 more)

### Community 41 - "ContextBudgetManager"
Cohesion: 0.33
Nodes (4): ContextBudgetManager, Budgets context window tokens and cleanly truncates at sentence boundaries., Heuristic token estimation (~4 chars per token)., Deduplicates overlapping content and trims chunks to fit within the token…

### Community 42 - "audit_security.py"
Cohesion: 0.29
Nodes (10): argparse, check_gitignore(), main(), Security audit script for KnowFlow AI. Checks for: 1. Exposed secrets /…, Scan Python source files for hardcoded credential patterns., Scan .env files for wildcard CORS and DEBUG=True in production configs., Verify that .env files are excluded from git tracking., scan_env_files() (+2 more)

### Community 43 - "Appendix B - Canonical Sources (read these before reinventing)"
Cohesion: 0.09
Nodes (21): APPENDICES - Real Source-Backed Reference Material, Appendix A - Install Commands per Design System, Appendix B - Canonical Sources (read these before reinventing), Appendix C - Apple Liquid Glass: Honest Web Approximation, Apple Liquid Glass (Apple platforms only), Atlassian, Bootstrap, Carbon (+13 more)

### Community 44 - "session.py"
Cohesion: 0.25
Nodes (8): async_sessionmaker, AsyncEngine, get_engine(), get_session_factory(), AsyncSession, Returns async SQLAlchemy engine if DATABASE_URL is configured., Returns the async sessionmaker factory., main()

### Community 46 - "extends"
Cohesion: 0.50
Nodes (3): extends, next/core-web-vitals, next/typescript

### Community 47 - "Design Audit"
Cohesion: 0.10
Nodes (19): Code Quality, Color and Surfaces, Component Patterns, Content, Design Audit, Fix Priority, How This Works, Iconography (+11 more)

### Community 50 - "Analysis & Synthesis Instructions"
Cohesion: 0.11
Nodes (18): 1. Define the Atmosphere, 2. Map the Color Palette, 3. Establish Typography Rules, 4. Define the Hero Section, 5. Describe Component Stylings, 6. Define Layout Principles, 7. Define Responsive Rules, 8. Encode Motion Philosophy (+10 more)

### Community 52 - "Agent Skill: Principal UI/UX Architect & Motion Choreographer (Awwwards-Tier)"
Cohesion: 0.11
Nodes (17): 1. Meta Information & Core Directive, 2. THE "ABSOLUTE ZERO" DIRECTIVE (STRICT ANTI-PATTERNS), 3. THE CREATIVE VARIANCE ENGINE, 4. HAPTIC MICRO-AESTHETICS (COMPONENT MASTERY), 5. MOTION CHOREOGRAPHY (FLUID DYNAMICS), 6. PERFORMANCE GUARDRAILS, 7. EXECUTION PROTOCOL, 8. PRE-OUTPUT CHECKLIST (+9 more)

### Community 53 - "Supabase"
Cohesion: 0.11
Nodes (15): Fix suggestion, Source, What happened, Skill Feedback, Steps, Core Principles, Debugging, Making and Committing Schema Changes (+7 more)

### Community 54 - "CORE DIRECTIVE: AWWWARDS-LEVEL IMAGE ART DIRECTION"
Cohesion: 0.12
Nodes (16): 10. SECTION RHYTHM RULE, 12. DENSITY & SPACING DISCIPLINE, 14. IMAGE / MEDIA DIRECTION, 16. MULTI-IMAGE CONSISTENCY RULE, 17. CLARITY CHECK, 19. RESPONSE BEHAVIOR, 1. ACTIVE BASELINE CONFIGURATION, 21. FINAL GOAL (+8 more)

### Community 55 - "SKILL: Industrial Brutalism & Tactical Telemetry UI"
Cohesion: 0.12
Nodes (16): 1. Skill Meta, 2.1 Swiss Industrial Print, 2.2 Tactical Telemetry & CRT Terminal, 2. Visual Archetypes, 3.1 Macro-Typography (Structural Headers), 3.2 Micro-Typography (Data & Telemetry), 3.3 Textural Contrast (Artistic Disruption), 3. Typographic Architecture (+8 more)

### Community 56 - "Changelog"
Cohesion: 0.12
Nodes (16): [1.2.0](https://github.com/supabase/agent-skills/compare/v1.1.1...v1.2.0) (2026-06-02), [1.3.0](https://github.com/supabase/agent-skills/compare/v1.2.0...v1.3.0) (2026-06-05), [1.4.0](https://github.com/supabase/agent-skills/compare/v1.3.0...v1.4.0) (2026-07-10), [1.5.0](https://github.com/supabase/agent-skills/compare/supabase-postgres-best-practices-v1.4.0...supabase-postgres-best-practices-v1.5.0) (2026-07-30), [1.6.0](https://github.com/supabase/agent-skills/compare/supabase-postgres-best-practices-v1.5.0...supabase-postgres-best-practices-v1.6.0) (2026-07-30), Bug Fixes, Bug Fixes, Bug Fixes (+8 more)

### Community 57 - "Changelog"
Cohesion: 0.12
Nodes (15): [0.1.3](https://github.com/supabase/agent-skills/compare/v0.1.2...v0.1.3) (2026-06-02), [0.1.4](https://github.com/supabase/agent-skills/compare/v0.1.3...v0.1.4) (2026-06-05), [0.1.5](https://github.com/supabase/agent-skills/compare/v0.1.4...v0.1.5) (2026-07-10), [0.1.6](https://github.com/supabase/agent-skills/compare/v0.1.5...supabase-v0.1.6) (2026-07-30), [0.1.7](https://github.com/supabase/agent-skills/compare/v0.1.6...supabase-v0.1.7) (2026-08-12), Bug Fixes, Bug Fixes, Bug Fixes (+7 more)

### Community 58 - "Writing Guidelines for Postgres References"
Cohesion: 0.12
Nodes (15): 1. Concrete Transformation Patterns, 2. Error-First Structure, 3. Quantified Impact, 4. Self-Contained Examples, 5. Semantic Naming, Code Example Standards, Comments, Impact Level Guidelines (+7 more)

### Community 59 - "Settings"
Cohesion: 0.32
Nodes (5): Settings, test_cors_origins_parsing(), test_default_settings(), BaseSettings, field_validator

### Community 60 - "Design System: Taste Standard"
Cohesion: 0.13
Nodes (14): 1. Visual Theme & Atmosphere, 2. Color Palette & Roles, 3. Typography Rules, 4. Component Stylings, 5. Hero Section, 6. Layout Principles, 7. Responsive Rules, 8. Motion & Interaction (Code-Phase Intent) (+6 more)

### Community 61 - "2. THE COMBINATORIAL VARIATION ENGINE"
Cohesion: 0.14
Nodes (14): 2. THE COMBINATORIAL VARIATION ENGINE, Background Character, Background Mode (per-section), Composition Anchor (per-section), CTA Variation, Hero Architecture, Hero Scale (per-page), Motion-Implied Language (+6 more)

### Community 62 - "export_openapi.py"
Cohesion: 0.29
Nodes (6): json, pydantic_settings, export_spec(), main(), Path, Export OpenAPI 3.1 specification for KnowFlow AI. Starts the FastAPI…

### Community 63 - "KnowFlow AI — Enterprise Knowledge & SOP Agent"
Cohesion: 0.04
Nodes (44): Domain Entity Model, KnowFlow AI — Architecture & Design Specification, Phase 1 Status: Foundation Verified, System Architecture, Common Interview Questions & Answers, Demo Scenario Flow (10-minute walkthrough), Files Reference, KnowFlow AI — Live Demo Guide (+36 more)

### Community 64 - "4. DESIGN ENGINEERING DIRECTIVES (Bias Correction)"
Cohesion: 0.17
Nodes (12): 4.10 Quotes & Testimonials, 4.11 Page Theme Lock (Light / Dark Mode Consistency), 4.1 Typography, 4.2 Color Calibration, 4.3 Layout Diversification, 4.4 Materiality, Shadows, Cards, 4.5 Interactive UI States, 4.6 Data & Form Patterns (+4 more)

### Community 65 - "endpoints/health.py"
Cohesion: 0.18
Nodes (12): app_schemas_health, get_health(), Returns application health status, database connectivity, and auth state. Real…, Deep readiness probe. Checks: - Database connectivity and pgvector extension…, readiness_probe(), check_database_health(), Any, Checks DB connectivity without crashing if unconfigured. (+4 more)

### Community 67 - "KnowFlow AI — Portfolio Case Study"
Cohesion: 0.20
Nodes (10): Core RAG Pipeline, Engineering Highlights for Resume, Evaluation Framework, Grounded Answering Policy, Key Design Decision: HybridReranker, KnowFlow AI — Portfolio Case Study, Project Summary, Source Code (+2 more)

### Community 68 - "10. REFERENCE VOCABULARY (Pattern Names the Agent Should Know)"
Cohesion: 0.20
Nodes (10): 10. REFERENCE VOCABULARY (Pattern Names the Agent Should Know), Animation Library Choice, Cards & Containers, Galleries & Media, Hero Paradigms, Layout & Grids, Micro-Interactions & Effects, Navigation & Menus (+2 more)

### Community 69 - "tasteskill: Anti-Slop Frontend Skill"
Cohesion: 0.20
Nodes (10): 13. OUT OF SCOPE, 14. FINAL PRE-FLIGHT CHECK, 1.A Dial Inference (design read → dial values), 1.B Use-Case Presets, 1.C How the Dials Drive Output, 1. THE THREE DIALS (Core Configuration), 2.A When to reach for a real design system (use official packages), 2.B When the brief is an aesthetic, not a system (+2 more)

### Community 70 - "CORE DIRECTIVE: AWWWARDS-LEVEL DESIGN ENGINEERING"
Cohesion: 0.20
Nodes (9): 1. PYTHON-DRIVEN TRUE RANDOMIZATION (BREAKING THE LOOP), 2. AIDA STRUCTURE & SPACING, 3. HERO ARCHITECTURE & THE 2-LINE IRON RULE, 4. THE GAPLESS BENTO GRID, 5. ADVANCED GSAP MOTION & HOVER PHYSICS, 6. COMPONENT ARSENAL & CREATIVITY, 7. CONTENT, ASSETS & STRICT BANS, 8. MANDATORY PRE-FLIGHT <design_plan> (+1 more)

### Community 71 - "22. STYLE VARIATION ENGINE"
Cohesion: 0.20
Nodes (10): 22. STYLE VARIATION ENGINE, Decorative Asset Set, Image Art Direction Bias, Motion-Implied Language, Palette Logic, Signature Component Set, Structure Bias, Texture / Surface Treatment (+2 more)

### Community 72 - "Protocol: Premium Utilitarian Minimalism UI Architect"
Cohesion: 0.20
Nodes (9): 1. Protocol Overview, 2. Absolute Negative Constraints (Banned Elements), 3. Typographic Architecture, 4. Color Palette (Warm Monochrome + Spot Pastels), 5. Component Specifications, 6. Iconography & Imagery Directives, 7. Subtle Motion & Micro-Animations, 8. Execution Protocol (+1 more)

### Community 73 - "Section Definitions"
Cohesion: 0.20
Nodes (9): 1. Query Performance (query), 2. Connection Management (conn), 3. Security & RLS (security), 4. Schema Design (schema), 5. Concurrency & Locking (lock), 6. Data Access Patterns (data), 7. Monitoring & Diagnostics (monitor), 8. Advanced Features (advanced) (+1 more)

### Community 75 - "11. COMPONENT EXECUTION GUIDELINES"
Cohesion: 0.22
Nodes (9): 11. COMPONENT EXECUTION GUIDELINES, 3D Cascading Card Deck, Diagonal Staggered Square Masonry, Hover-Accordion Slice Layout, Off-Grid Editorial Layout, Pristine Gapless Bento Grid, Product UI Panel Stack, Turning Polaroid Arc (+1 more)

### Community 76 - "18. EXTRA CREATIVITY & IMPLEMENTATION EDGE"
Cohesion: 0.22
Nodes (9): 18. EXTRA CREATIVITY & IMPLEMENTATION EDGE, Composition variety check, Conversion focus, Cross-section contrast, CTA specificity, Cultural / tonal alignment, Data-viz restraint, Image variety inside one comp (+1 more)

### Community 77 - "Ponytail"
Cohesion: 0.22
Nodes (8): Boundaries, Intensity, Output, Persistence, Ponytail, Rules, The ladder, When NOT to be lazy

### Community 78 - "context.py"
Cohesion: 0.24
Nodes (11): app_api_v1_endpoints, app_api_v1_router, app_db_session, app_schemas_search, Evaluation API Endpoints for KnowFlow AI. Runs automated RAG evaluation…, Request-scoped user context dependency. In PRODUCTION (settings.ENVIRONMENT ==…, get_db(), FastAPI dependency for DB sessions. Raises RuntimeError if DB is unconfigured. (+3 more)

### Community 80 - "9. AI TELLS (Forbidden Patterns)"
Cohesion: 0.25
Nodes (8): 9.A Visual & CSS, 9. AI TELLS (Forbidden Patterns), 9.B Typography, 9.C Layout & Spacing, 9.D Content & Data ("Jane Doe" Effect), 9.E External Resources & Components, 9.F Production-Test Tells (banned outright), 9.G EM-DASH BAN (the single most-violated Tell)

### Community 81 - "12. THE COMBINATORIAL VARIATION ENGINE"
Cohesion: 0.25
Nodes (8): 12. THE COMBINATORIAL VARIATION ENGINE, Background Character, Hero Architecture, Motion-Implied Language, Section System, Signature Component Set, Theme Paradigm, Typography Character

### Community 82 - "8. ANTI-AI-SLOP RULES"
Cohesion: 0.25
Nodes (8): 8. ANTI-AI-SLOP RULES, Carousel / marquee slop (layout), Content slop, Data / KPI slop, Density slop, Layout slop, Typography slop, Visual slop

### Community 83 - "Ponytail Help"
Cohesion: 0.25
Nodes (7): Configure Default Mode, Deactivate, Levels, More, Ponytail Help, Skills, Update

### Community 86 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, eslint, eslint-config-next, postcss, tailwindcss, @types/node, @types/react, @types/react-dom (+1 more)

### Community 87 - "11. REDESIGN PROTOCOL"
Cohesion: 0.29
Nodes (7): 11.A Detect the Mode (first action), 11.B Audit Before Touching, 11.C Preservation Rules, 11.D Modernisation Levers (priority order), 11.E Decision Tree: Targeted Evolution vs Full Redesign, 11.F What Never Changes Silently, 11. REDESIGN PROTOCOL

### Community 88 - "3. DEFAULT ARCHITECTURE & CONVENTIONS"
Cohesion: 0.29
Nodes (7): 3.A Stack, 3.B State, 3.C Icons, 3.D Emoji Policy, 3. DEFAULT ARCHITECTURE & CONVENTIONS, 3.E Responsiveness & Layout Mechanics, 3.F Dependency Verification (mandatory)

### Community 89 - "6. PERFORMANCE & ACCESSIBILITY GUARDRAILS"
Cohesion: 0.29
Nodes (7): 6.A Hardware Acceleration, 6.B Reduced Motion (mandatory), 6.C Dark Mode (mandatory for any consumer-facing page), 6.D Core Web Vitals Targets, 6.E DOM Cost, 6.F Z-Index Restraint, 6. PERFORMANCE & ACCESSIBILITY GUARDRAILS

### Community 90 - "Full-Output Enforcement"
Cohesion: 0.29
Nodes (6): Banned Output Patterns, Baseline, Execution Process, Full-Output Enforcement, Handling Long Outputs, Quick Check

### Community 91 - "33. CATEGORY-SPECIFIC BIAS"
Cohesion: 0.29
Nodes (7): 33. CATEGORY-SPECIFIC BIAS, Commerce, Fintech, Health / Fitness, Productivity, Social, Wellness / Lifestyle

### Community 92 - "13. COLOR & MATERIAL RULES"
Cohesion: 0.29
Nodes (7): 13. COLOR & MATERIAL RULES, Background Confidence Rule, Background-image harmony, Gradient Discipline, Materiality, Palette Discipline, Strong guidance

### Community 93 - "4. HERO MINIMALISM RULES"
Cohesion: 0.29
Nodes (7): 4. HERO MINIMALISM RULES, Absolute Hero Rules, Graphic Restraint, Headline Rule, Hero Composition Bias, Pre-output check, Typography Execution

### Community 94 - "require_admin"
Cohesion: 0.23
Nodes (7): Dependency: rejects non-admin callers with HTTP 403. Use this on all admin-only…, require_admin(), asyncio, Verify that missing tokens cause 401 in production., TestProductionFailClosed, TestRequireAdminDependency, Production Hardening Implemented

### Community 95 - "29. ANTI-AI-SLOP RULES"
Cohesion: 0.33
Nodes (6): 29. ANTI-AI-SLOP RULES, Content slop, Density slop, Layout slop, Typography slop, Visual slop

### Community 96 - "5. IMAGE COUNT & PAGE SLICING"
Cohesion: 0.33
Nodes (6): 5. IMAGE COUNT & PAGE SLICING, Continuity Rule, Counting rule, Format, Section size variety, THIS IS THE PRIMARY OUTPUT RULE

### Community 97 - "Supabase Postgres Best Practices"
Cohesion: 0.33
Nodes (5): How to Use, References, Rule Categories by Priority, Supabase Postgres Best Practices, When to Apply

### Community 98 - "time"
Cohesion: 0.15
Nodes (15): concurrent_futures, docx, dotenv, os, playwright_sync_api, reportlab_lib, reportlab_lib_pagesizes, reportlab_lib_styles (+7 more)

### Community 100 - "0. BRIEF INFERENCE (Read the Room Before Anything Else)"
Cohesion: 0.40
Nodes (5): 0.A Read these signals first, 0.B Output a one-line "Design Read" before generating, 0. BRIEF INFERENCE (Read the Room Before Anything Else), 0.C If the brief is ambiguous, ask one question, do not guess, 0.D Anti-Default Discipline

### Community 101 - "12. THE BLOCK LIBRARY (Contract - Implementations Land Here Iteratively)"
Cohesion: 0.40
Nodes (5): 12.A File Location, 12.B Required Frontmatter, 12.C Required Body Sections, 12.D Block-Library Discipline, 12. THE BLOCK LIBRARY (Contract - Implementations Land Here Iteratively)

### Community 102 - "5. CONTEXT-AWARE PROACTIVITY"
Cohesion: 0.40
Nodes (5): 5.A Sticky-Stack - Canonical Skeleton, 5.B Horizontal-Pan - Canonical Skeleton, 5.C Scroll-Reveal Stagger - Canonical Skeleton (lighter alternative), 5. CONTEXT-AWARE PROACTIVITY, 5.D Forbidden Animation Patterns

### Community 103 - "8. DARK MODE PROTOCOL"
Cohesion: 0.40
Nodes (5): 8.A Token Strategy (pick one, stick to it), 8.B Do Not Prescribe Specific Colors Here, 8.C Default Mode, 8.D Test in Both Modes Before Finishing, 8. DARK MODE PROTOCOL

### Community 104 - "21. MOBILE ANTI-AI-TELLS RULE"
Cohesion: 0.40
Nodes (5): 21. MOBILE ANTI-AI-TELLS RULE, Copy AI tells, Layout AI tells, UI clutter tells, Visual AI tells

### Community 105 - "ponytail-audit/SKILL.md"
Cohesion: 0.40
Nodes (4): Boundaries, Hunt, Output, Tags

### Community 106 - "Ponytail Gain"
Cohesion: 0.40
Nodes (4): Boundaries, Honesty boundary, Ponytail Gain, Scoreboard

### Community 107 - "ponytail-review/SKILL.md"
Cohesion: 0.40
Nodes (4): Boundaries, Examples, Format, Scoring

### Community 108 - "logging"
Cohesion: 0.12
Nodes (15): app_core_config, AuthProvider, ABC, Any, Abstract interface for authentication providers. Prevents hardcoding Supabase…, Verifies bearer token and returns AuthUser or None., Returns auth provider status and configuration state., get_auth_provider() (+7 more)

### Community 109 - "CLINICAL OPERATIONS SOP: REFRIGERATED STORAGE & COLD CHAIN INTEGRITY"
Cohesion: 0.40
Nodes (4): 1. Temperature Specifications and Monitoring, 2. Temperature Excursion Management, 3. Quarantine and Disposition Protocol, CLINICAL OPERATIONS SOP: REFRIGERATED STORAGE & COLD CHAIN INTEGRITY

### Community 111 - "Challenges & Learning"
Cohesion: 0.33
Nodes (5): Returns True ONLY in non-production environments., Challenge 1: Grounding without hallucination, Challenge 2: Accurate NDCG normalization, Challenge 3: Authentication fail-closed vs. developer experience, Challenges & Learning

### Community 112 - "7. DIAL DEFINITIONS (Technical Reference)"
Cohesion: 0.50
Nodes (4): 7. DIAL DEFINITIONS (Technical Reference), DESIGN_VARIANCE (Level 1-10), MOTION_INTENSITY (Level 1-10), VISUAL_DENSITY (Level 1-10)

### Community 113 - "33. DEFAULT SECTION PACKS"
Cohesion: 0.50
Nodes (4): 12-section pack, 33. DEFAULT SECTION PACKS, 4-section pack, 8-section pack

### Community 114 - "14. HERO MINIMALISM RULES"
Cohesion: 0.50
Nodes (4): 14. HERO MINIMALISM RULES, Absolute Hero Rules, Headline Rule, Hero Cleanliness Rule

### Community 115 - "37. EXAMPLE INTERPRETATIONS"
Cohesion: 0.50
Nodes (4): 37. EXAMPLE INTERPRETATIONS, Example 1, Example 2, Example 3

### Community 116 - "2. PLATFORM MODE RULE"
Cohesion: 0.50
Nodes (4): 2. PLATFORM MODE RULE, Android-native premium, Cross-platform premium neutral, iOS-native premium

### Community 117 - "37. EXAMPLE INTERPRETATIONS"
Cohesion: 0.50
Nodes (4): 37. EXAMPLE INTERPRETATIONS, Example 1, Example 2, Example 3

### Community 118 - "15. DEFAULT SITE PACKS"
Cohesion: 0.50
Nodes (4): 12-section pack, 15. DEFAULT SITE PACKS, 4-section pack, 8-section pack

### Community 119 - "20. EXAMPLE INTERPRETATIONS"
Cohesion: 0.50
Nodes (4): 20. EXAMPLE INTERPRETATIONS, Example 1, Example 2, Example 3

### Community 120 - "ponytail-debt/SKILL.md"
Cohesion: 0.50
Nodes (3): Boundaries, Output, Scan

### Community 121 - "sentry.py"
Cohesion: 0.25
Nodes (8): init_sentry(), Any, Sentry SDK integration for production error tracking. Initializes only when…, Strip PII / document content from Sentry event payloads., Initialize Sentry SDK with PII filtering. Args: dsn: Sentry Data Source Name…, _scrub_event(), _redact(), lifespan()

### Community 122 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 123 - "backend-status-indicator.tsx"
Cohesion: 0.53
Nodes (4): BackendStatusIndicator(), SystemHealthBadge(), fetchSystemHealth(), HealthData

## Knowledge Gaps
- **686 isolated node(s):** `next/core-web-vitals`, `next/typescript`, `nextConfig`, `name`, `version` (+681 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1034 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **39 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `require_admin()` connect `require_admin` to `endpoints/chat.py`, `UserContext`, `context.py`, `test_production_auth.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `KnowFlow AI — Portfolio Case Study` connect `KnowFlow AI — Portfolio Case Study` to `Challenges & Learning`, `require_admin`, `KnowFlow AI — Enterprise Knowledge & SOP Agent`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `Production Hardening Implemented` connect `require_admin` to `KnowFlow AI — Portfolio Case Study`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `UserContext` (e.g. with `get_admin_stats()` and `get_audit_logs()`) actually correct?**
  _`UserContext` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `RankedChunk` (e.g. with `GroundingEvaluator` and `BaseLLMProvider`) actually correct?**
  _`RankedChunk` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Base` (e.g. with `init_db()` and `test_document_chunk_model_fields()`) actually correct?**
  _`Base` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `next/core-web-vitals`, `next/typescript`, `nextConfig` to the rest of the system?**
  _686 weakly-connected nodes found - possible documentation gaps or missing edges._