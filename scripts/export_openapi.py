#!/usr/bin/env python3
"""
Export OpenAPI 3.1 specification for KnowFlow AI.

Starts the FastAPI application, fetches /openapi.json, and writes
the result to docs/openapi.json.

Usage:
    python scripts/export_openapi.py
    python scripts/export_openapi.py --output docs/openapi.json --pretty
"""
import argparse
import json
import os
import sys
from pathlib import Path

# Add backend to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "backend"))

os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NEXT_PUBLIC_SUPABASE_URL", "")
os.environ.setdefault("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "")
os.environ.setdefault("LLM_API_KEY", "")
os.environ.setdefault("EMBEDDING_API_KEY", "")


def export_spec(output_path: Path, pretty: bool) -> None:
    from app.main import app  # type: ignore  # noqa: PLC0415

    spec = app.openapi()
    indent = 2 if pretty else None
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(spec, indent=indent), encoding="utf-8")
    print(f"[OK] OpenAPI spec exported to: {output_path} ({output_path.stat().st_size} bytes)")

    # Print summary
    paths = spec.get("paths", {})
    schemas = spec.get("components", {}).get("schemas", {})
    print(f"   Endpoints: {len(paths)}")
    print(f"   Schemas:   {len(schemas)}")
    print(f"   OpenAPI version: {spec.get('openapi', 'unknown')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export KnowFlow AI OpenAPI specification")
    parser.add_argument("--output", default=str(ROOT / "docs" / "openapi.json"), help="Output file path")
    parser.add_argument("--pretty", action="store_true", default=True, help="Pretty-print JSON output")
    args = parser.parse_args()

    export_spec(Path(args.output), args.pretty)


if __name__ == "__main__":
    main()
