#!/usr/bin/env python3
"""
Security audit script for KnowFlow AI.

Checks for:
1. Exposed secrets / credentials in the working tree.
2. Dangerous wildcard CORS origins in .env files.
3. DEBUG=True in any production-tagged environment file.
4. Hardcoded credential patterns in Python source files.

Usage:
    python scripts/audit_security.py
    python scripts/audit_security.py --strict   # exits non-zero on any warning
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# ------------------------------------------------------------------ #
# Patterns that indicate exposed secrets                              #
# ------------------------------------------------------------------ #
_SECRET_PATTERNS = [
    (r"sk-[A-Za-z0-9]{20,}", "OpenAI API key"),
    (r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", "JWT token"),
    (r"(?:password|passwd|secret|api_key)\s*=\s*['\"][^'\"]{8,}['\"]", "Hardcoded credential"),
    (r"(?:SUPABASE_SERVICE_ROLE_KEY|SUPABASE_ANON_KEY)\s*=\s*['\"]eyJ[A-Za-z0-9._-]+['\"]", "Supabase key in source"),
]

_DANGER_WILDCARD_CORS = re.compile(r'CORS_ORIGINS.*\*')
_DEBUG_PRODUCTION = re.compile(r'DEBUG\s*=\s*[Tt]rue', re.IGNORECASE)

ISSUES: list[dict] = []


def warn(severity: str, file_path: str, line_no: int, message: str) -> None:
    ISSUES.append({"severity": severity, "file": file_path, "line": line_no, "message": message})
    tag = "[ERROR]" if severity == "error" else "[ WARN]"
    print(f"{tag}  {file_path}:{line_no}  {message}")


def scan_python_sources() -> None:
    """Scan Python source files for hardcoded credential patterns."""
    print("\n[1/3] Scanning Python source files for credential patterns...")
    py_files = list(ROOT.rglob("*.py"))
    checked = 0
    for path in py_files:
        # Skip venv, __pycache__, migrations
        if any(part in path.parts for part in ("venv", "__pycache__", "migrations", ".git")):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        checked += 1
        for line_no, line in enumerate(content.splitlines(), 1):
            for pattern, label in _SECRET_PATTERNS:
                if re.search(pattern, line):
                    warn("error", str(path.relative_to(ROOT)), line_no, f"{label} found in source code")
    print(f"   Scanned {checked} Python files.")


def scan_env_files() -> None:
    """Scan .env files for wildcard CORS and DEBUG=True in production configs."""
    print("\n[2/3] Scanning .env files for dangerous settings...")
    env_files = list(ROOT.rglob(".env*"))
    for path in env_files:
        if any(part in path.parts for part in ("venv", ".git")):
            continue
        if path.name.endswith((".example", ".sample", ".template")):
            continue  # Template files are expected to have placeholders
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for line_no, line in enumerate(content.splitlines(), 1):
            if _DANGER_WILDCARD_CORS.search(line):
                warn("error", str(path.relative_to(ROOT)), line_no, "Wildcard CORS origin (*) is dangerous in production")
            if "production" in str(path).lower() and _DEBUG_PRODUCTION.search(line):
                warn("error", str(path.relative_to(ROOT)), line_no, "DEBUG=True in a production environment file")
    print(f"   Scanned {len(env_files)} .env* files.")


def check_gitignore() -> None:
    """Verify that .env files are excluded from git tracking."""
    print("\n[3/3] Checking .gitignore for .env exclusion...")
    gitignore = ROOT / ".gitignore"
    if not gitignore.exists():
        warn("warn", ".gitignore", 0, ".gitignore file not found — .env files may be committed")
        return
    content = gitignore.read_text(encoding="utf-8", errors="replace")
    if ".env" not in content:
        warn("error", ".gitignore", 0, ".env pattern not found in .gitignore — secrets may be committed")
    else:
        print(f"   [OK] .env is excluded from git tracking")


def main() -> int:
    parser = argparse.ArgumentParser(description="KnowFlow AI security audit script")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on any warning")
    args = parser.parse_args()

    print("=" * 60)
    print("KnowFlow AI — Security Audit")
    print("=" * 60)

    scan_python_sources()
    scan_env_files()
    check_gitignore()

    print("\n" + "=" * 60)
    errors = [i for i in ISSUES if i["severity"] == "error"]
    warnings = [i for i in ISSUES if i["severity"] == "warn"]
    print(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s)")

    if errors:
        print("\n[FAIL] Security audit FAILED - resolve errors before deploying to production.")
        return 1

    if args.strict and warnings:
        print("\n[WARN] Security audit completed with warnings (--strict mode).")
        return 1

    print("\n[OK] Security audit passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
