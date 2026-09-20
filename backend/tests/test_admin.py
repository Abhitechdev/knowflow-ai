from starlette.testclient import TestClient


def test_admin_stats_endpoint(client: TestClient):
    res = client.get("/api/v1/admin/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_documents" in data
    assert "total_chunks" in data
    assert "total_conversations" in data
    assert "total_messages" in data
    assert "total_audit_events" in data
    assert "positive_feedback_count" in data
    assert "negative_feedback_count" in data
    assert data["grounded_answering_policy"] == "Active"
    assert data["hybrid_reranker_status"] == "Enabled"


def test_admin_audit_logs_endpoint(client: TestClient):
    res = client.get("/api/v1/admin/audit-logs?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


def test_evaluation_summary_endpoint(client: TestClient):
    res = client.get("/api/v1/evaluation/summary")
    assert res.status_code == 200
    data = res.json()
    assert data is None or "total_cases" in data
