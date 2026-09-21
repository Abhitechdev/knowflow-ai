import json
from pathlib import Path
from starlette.testclient import TestClient

from app.core.sentry import _scrub_event, init_sentry
from app.main import app


def test_sentry_pii_scrubbing():
    """Verify that _scrub_event recursively redacts sensitive fields and PII."""
    raw_event = {
        "user": {"id": "usr-123", "email": "user@example.com"},
        "extra": {
            "query": "What is the secret formula for Project X?",
            "content": "Confidential patient record data",
            "chunk": "Chunk text containing proprietary formula",
            "answer": "Here is the proprietary answer",
            "context": "Context snippet with private data",
            "message": "Direct message with sensitive details",
            "messages": ["msg1", "msg2"],
            "password": "supersecretpassword",
            "token": "eyJh...sensitive_jwt_token",
            "authorization": "Bearer eyJh...",
            "cookie": "session_id=123456",
            "secret": "my-vault-secret",
            "api_key": "sk-1234567890",
            "safe_metadata": {
                "document_id": "doc-456",
                "nested_sensitive": {
                    "password": "another_nested_password",
                    "chunk": "nested chunk data",
                },
            },
            "array_of_objects": [
                {"token": "token_in_list", "public_id": "pub-001"},
                {"query": "query_in_list", "count": 5},
            ],
        },
    }

    scrubbed = _scrub_event(raw_event, {})

    # Check root sensitive fields
    extra = scrubbed["extra"]
    assert extra["query"] == "[Filtered]"
    assert extra["content"] == "[Filtered]"
    assert extra["chunk"] == "[Filtered]"
    assert extra["answer"] == "[Filtered]"
    assert extra["context"] == "[Filtered]"
    assert extra["message"] == "[Filtered]"
    assert extra["messages"] == "[Filtered]"
    assert extra["password"] == "[Filtered]"
    assert extra["token"] == "[Filtered]"
    assert extra["authorization"] == "[Filtered]"
    assert extra["cookie"] == "[Filtered]"
    assert extra["secret"] == "[Filtered]"
    assert extra["api_key"] == "[Filtered]"

    # Check non-sensitive field preserved
    assert extra["safe_metadata"]["document_id"] == "doc-456"

    # Check nested dict scrubbing
    assert extra["safe_metadata"]["nested_sensitive"]["password"] == "[Filtered]"
    assert extra["safe_metadata"]["nested_sensitive"]["chunk"] == "[Filtered]"

    # Check list element scrubbing
    assert extra["array_of_objects"][0]["token"] == "[Filtered]"
    assert extra["array_of_objects"][0]["public_id"] == "pub-001"
    assert extra["array_of_objects"][1]["query"] == "[Filtered]"
    assert extra["array_of_objects"][1]["count"] == 5


def test_sentry_initialization_safety():
    """Verify init_sentry handles empty DSN and missing package safely without crashing."""
    # 1. Empty DSN is a clean no-op
    init_sentry(dsn="", environment="test", release="1.0.0")

    # 2. Non-empty DSN handles missing sentry_sdk gracefully (logs warning, does not throw)
    init_sentry(dsn="https://fake_dsn@sentry.io/12345", environment="test", release="1.0.0")


def test_health_liveness_endpoint(client: TestClient):
    """Verify /api/health/live process liveness probe."""
    res = client.get("/api/health/live")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "alive"
    assert "timestamp" in data


def test_health_readiness_endpoint(client: TestClient):
    """Verify /api/health/ready deep readiness probe."""
    res = client.get("/api/health/ready")
    assert res.status_code in (200, 503)
    data = res.json()
    assert "ready" in data
    assert "checks" in data
    assert "database" in data["checks"]
    assert "auth" in data["checks"]
    assert "app" in data["checks"]
    assert "timestamp" in data


def test_health_overall_endpoint(client: TestClient):
    """Verify /api/health overall status endpoint."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "degraded")
    assert "version" in data
    assert "environment" in data
    assert "database" in data
    assert "auth" in data
    assert "timestamp" in data


def test_root_endpoint(client: TestClient):
    """Verify root endpoint structure."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "service" in data
    assert "version" in data
    assert "environment" in data
    assert data["health"] == "/api/health"


def test_openapi_contract_drift():
    """
    Automated API Contract Drift Guard:
    Verifies that the committed docs/openapi.json specification exactly matches
    the live application's generated OpenAPI specification at test execution time.
    """
    root_dir = Path(__file__).resolve().parent.parent.parent
    spec_path = root_dir / "docs" / "openapi.json"

    assert spec_path.exists(), f"OpenAPI specification not found at {spec_path}"

    committed_spec = json.loads(spec_path.read_text(encoding="utf-8"))
    live_spec = app.openapi()

    assert live_spec == committed_spec, (
        "API contract drift detected! The live FastAPI application schema differs from "
        "the committed docs/openapi.json specification. Run 'python scripts/export_openapi.py' "
        "to synchronize the specification."
    )
