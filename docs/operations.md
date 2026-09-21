# KnowFlow AI — Operations & Maintenance Manual

## 1. Health Probes & Monitoring

KnowFlow AI exposes dedicated health and readiness endpoints for cloud orchestrators (Render, Kubernetes, load balancers):

| Endpoint | Purpose | Success Condition | Response Schema |
|---|---|---|---|
| `GET /api/health` | Overall system diagnostic | HTTP 200 | `{"status": "healthy", "database": {"connected": true}, "auth": {...}}` |
| `GET /api/health/live` | Liveness probe (process alive) | HTTP 200 | `{"status": "alive"}` |
| `GET /api/health/ready` | Readiness probe (traffic ready) | HTTP 200 | `{"ready": true, "database": true}` |

### 1.1 Monitoring Recommendations
- Configure external HTTP uptime monitors (e.g. BetterStack, Pingdom) to poll `GET /api/health/ready` at 60-second intervals.
- Alert threshold: 3 consecutive non-200 responses or latency $> 3000\text{ ms}$.

---

## 2. Database Migrations (Alembic)

Database schema migrations are managed via Alembic.

### 2.1 Applying Migrations
To upgrade the database to the latest schema:
```bash
cd backend
alembic upgrade head
```

### 2.2 Reverting Migrations
To roll back the most recent migration:
```bash
cd backend
alembic downgrade -1
```

### 2.3 Creating New Migrations
```bash
cd backend
alembic revision --autogenerate -m "describe_change"
```

---

## 3. Disaster Recovery & Backup Runbook

### 3.1 Backup Strategy
- **Automated Physical Backups**: Managed by Supabase Cloud with continuous Write-Ahead Log (WAL) archiving for Point-In-Time Recovery (PITR $\le 5$ min).
- **Logical Schema & Data Dumps**: Performed via `scripts/backup_db.py` producing a compressed SQL/custom archive.

```bash
python scripts/backup_db.py --output backups/knowflow_backup.dump
```

### 3.2 Restore & Recovery Verification
- Tested and verified under Gate 5F-2.
- **Empirical Restore Duration**: **28.08 seconds** (16/16 tables restored with full SHA-256 state parity and pgvector 384-dimensional vector indexing intact).
- **Modeled Operational RTO**: **12.47 minutes** (combining automated detection, sandbox provisioning, physical restore, and validation probes).

```bash
python scripts/test_restore.py --backup backups/knowflow_backup.dump --target-db "$DISPOSABLE_DB_URL"
```

---

## 4. Audit Logging & Compliance Records

- Sensitive operations (User logins, document uploads, document deletions, role modifications) generate immutable records in the `audit_logs` table.
- Audit records store:
  - `id`: UUID
  - `workspace_id`: Multi-tenant boundary
  - `user_id`: Acting actor
  - `action`: `DOCUMENT_UPLOADED`, `DOCUMENT_DELETED`, `USER_LOGIN`, etc.
  - `metadata_json`: Sanitized context (document title, storage path, timestamp). Secret credentials and document body texts are strictly omitted.
