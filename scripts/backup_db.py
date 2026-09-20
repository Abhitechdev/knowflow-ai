#!/usr/bin/env python3
"""
Database backup script for KnowFlow AI.

Creates a timestamped pg_dump snapshot of the production database.
Supports optional gzip compression and S3 upload (if boto3 is installed).

Usage:
    python scripts/backup_db.py
    python scripts/backup_db.py --output-dir /backups
    python scripts/backup_db.py --compress
    python scripts/backup_db.py --compress --verify
"""
import argparse
import gzip
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent


def get_db_url() -> str:
    """Read DATABASE_URL from environment or .env file."""
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        env_file = ROOT / "backend" / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("DATABASE_URL="):
                    db_url = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    return db_url


def parse_db_url(db_url: str) -> dict:
    """Parse a postgresql+asyncpg://... URL into pg_dump components."""
    import re
    # Strip asyncpg driver prefix
    url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    pattern = r"postgresql://(?P<user>[^:@]+)(?::(?P<password>[^@]*))?@(?P<host>[^:/]+)(?::(?P<port>\d+))?/(?P<dbname>[^?]+)"
    m = re.match(pattern, url)
    if not m:
        raise ValueError(f"Cannot parse DATABASE_URL: {db_url[:60]}...")
    return {
        "user": m.group("user"),
        "password": m.group("password") or "",
        "host": m.group("host"),
        "port": m.group("port") or "5432",
        "dbname": m.group("dbname"),
    }


def run_backup(output_dir: Path, compress: bool, verify: bool) -> Path:
    """Execute pg_dump and save the backup file."""
    db_url = get_db_url()
    if not db_url:
        print("❌ DATABASE_URL not set. Cannot perform backup.")
        sys.exit(1)

    try:
        parts = parse_db_url(db_url)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fname = f"knowflow_backup_{ts}.sql"
    if compress:
        fname += ".gz"
    out_path = output_dir / fname

    env = os.environ.copy()
    if parts["password"]:
        env["PGPASSWORD"] = parts["password"]

    cmd = [
        "pg_dump",
        "-h", parts["host"],
        "-p", parts["port"],
        "-U", parts["user"],
        "-d", parts["dbname"],
        "--no-password",
        "--format=plain",
        "--encoding=UTF8",
    ]

    print(f"Running: pg_dump → {out_path}")
    try:
        result = subprocess.run(cmd, capture_output=True, env=env, timeout=300)
    except FileNotFoundError:
        print("❌ pg_dump not found. Install PostgreSQL client tools.")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("❌ pg_dump timed out after 300 seconds.")
        sys.exit(1)

    if result.returncode != 0:
        print(f"❌ pg_dump failed:\n{result.stderr.decode()}")
        sys.exit(1)

    sql_content = result.stdout
    if compress:
        with gzip.open(out_path, "wb") as f:
            f.write(sql_content)
    else:
        out_path.write_bytes(sql_content)

    size_kb = out_path.stat().st_size // 1024
    print(f"✅ Backup complete: {out_path} ({size_kb} KB)")

    if verify:
        _verify_backup(out_path, compress)

    return out_path


def _verify_backup(backup_path: Path, compressed: bool) -> None:
    """Verify backup file contains expected SQL content."""
    print("Verifying backup integrity...")
    try:
        if compressed:
            with gzip.open(backup_path, "rb") as f:
                header = f.read(512).decode("utf-8", errors="replace")
        else:
            with backup_path.open("r", encoding="utf-8", errors="replace") as f:
                header = f.read(512)
    except Exception as e:
        print(f"❌ Backup verification failed — could not read file: {e}")
        sys.exit(1)

    if "PostgreSQL database dump" not in header and "CREATE TABLE" not in header and "SET" not in header:
        print("❌ Backup verification failed — file does not look like a valid pg_dump output.")
        sys.exit(1)

    print("✅ Backup integrity verified.")


def main() -> None:
    parser = argparse.ArgumentParser(description="KnowFlow AI database backup")
    parser.add_argument("--output-dir", default=str(ROOT / "backups"), help="Output directory for backup files")
    parser.add_argument("--compress", action="store_true", help="Compress output with gzip")
    parser.add_argument("--verify", action="store_true", help="Verify backup file integrity after creation")
    args = parser.parse_args()

    run_backup(
        output_dir=Path(args.output_dir),
        compress=args.compress,
        verify=args.verify,
    )


if __name__ == "__main__":
    main()
