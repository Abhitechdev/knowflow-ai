def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "KnowFlow AI"
    assert "version" in data
    assert data["health"] == "/api/health"


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert "version" in data
    assert "environment" in data
    assert "database" in data
    assert "auth" in data
    assert "timestamp" in data
    # In local dev without DATABASE_URL, database status must report 'unconfigured', not fake healthy
    assert data["database"]["status"] in ("unconfigured", "healthy", "disconnected")


def test_v1_health_alias(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
