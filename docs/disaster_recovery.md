# Disaster Recovery Runbook — KnowFlow AI

## Overview

This document describes the backup, recovery, and failover procedures for the KnowFlow AI production database. Targets are operational goals — **not guaranteed SLAs**.

| Metric | Target |
|--------|--------|
| **RTO** (Recovery Time Objective) | ≤ 30 minutes |
| **RPO** (Recovery Point Objective) | ≤ 1 hour |

RTO and RPO are validated periodically by running the restore verification script. Results are benchmark measurements, not unconditional guarantees.

---

## Backup Strategy

### Automated Daily pg_dump Backup

```bash
# Compress and verify a full database dump
python scripts/backup_db.py --compress --verify --output-dir /backups
```

Recommended cron schedule:

```cron
0 2 * * * cd /app && python scripts/backup_db.py --compress --verify >> /var/log/knowflow-backup.log 2>&1
```

Backup files are named: `knowflow_backup_YYYYMMDDTHHMMSSZ.sql.gz`

### Supabase Point-in-Time Recovery (PITR)

Supabase Pro/Enterprise plans provide PITR with up to 7-day retention. To restore to a specific timestamp:

1. Log in to the [Supabase Dashboard](https://app.supabase.com).
2. Navigate to **Settings → Database → Point in Time Recovery**.
3. Select a target timestamp and initiate the restore.
4. After restore completes, run the application health check:
   ```bash
   curl https://api.your-domain.com/api/health/ready
   ```

---

## Restore Verification

Run the actual restore test against a staging environment to validate RTO:

```bash
# Dry-run (validates tool availability only — safe to run in CI)
python scripts/test_restore.py --dry-run

# Full restore cycle (requires database credentials)
DATABASE_URL=postgresql://... python scripts/test_restore.py
```

The script will:
1. Create a pg_dump of the source database.
2. Spin up a temporary restore database.
3. Restore the dump and validate row integrity.
4. Report elapsed time vs. the RTO target.
5. Drop the temporary database.

Run this test **at least monthly** and after major schema migrations.

---

## Emergency Failover Procedure

In the event of a critical database failure:

### Step 1: Confirm the incident (< 5 minutes)
```bash
# Check health
curl https://api.your-domain.com/api/health/ready

# Check Supabase status
open https://status.supabase.com
```

### Step 2: Assess recovery path (< 5 minutes)

| Scenario | Action |
|----------|--------|
| Supabase service outage | Wait for Supabase recovery; monitor status page |
| Data corruption / accidental deletion | Trigger PITR restore from Dashboard |
| Schema corruption | Restore from last pg_dump snapshot |
| Connection pooler failure | Switch connection string to direct port (5432) |

### Step 3: Execute restore (< 20 minutes)

For a pg_dump restore:

```bash
# 1. Download the latest backup
ls -lt /backups/ | head -5

# 2. Restore to a fresh database
createdb -h HOST -U USER knowflow_restore_test
gunzip -c knowflow_backup_TIMESTAMP.sql.gz | psql -h HOST -U USER -d knowflow_restore_test

# 3. Verify row counts match expectations
psql -h HOST -U USER -d knowflow_restore_test -c "SELECT COUNT(*) FROM documents;"

# 4. Update DATABASE_URL to point to the restored database
# 5. Restart the application
```

### Step 4: Verify (< 5 minutes)

```bash
curl https://api.your-domain.com/api/health/ready
# Expected: {"ready": true, ...}
```

---

## Connection Configuration

| Use Case | Connection String Port |
|----------|----------------------|
| Application API (stateless) | 6543 (Supabase transaction pooler) |
| Alembic migrations | 5432 (direct connection) |
| Backup / restore scripts | 5432 (direct connection) |

Configure `statement_timeout` to prevent runaway queries:

```sql
-- Applied via Alembic or Supabase SQL Editor
ALTER DATABASE knowflow SET statement_timeout = '8s';
```

---

## Backup Retention Policy

| Backup Type | Retention |
|-------------|-----------|
| Daily pg_dump | 30 days |
| Supabase PITR | 7 days (Pro plan) |

---

## Validation Schedule

| Test | Frequency |
|------|-----------|
| Restore verification (`test_restore.py`) | Monthly |
| Backup integrity check (`backup_db.py --verify`) | Daily (automated) |
| Health probe verification | Continuous (load balancer) |
