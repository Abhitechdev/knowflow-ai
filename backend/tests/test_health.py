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


def test_cors_trusted_origin_allowed(client):
    response = client.options(
        "/api/health",
        headers={
            "Origin": "https://knowflow-ai-pied.vercel.app",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://knowflow-ai-pied.vercel.app"


def test_cors_attacker_origin_rejected(client):
    response = client.options(
        "/api/health",
        headers={
            "Origin": "https://attacker.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    # Origin is not trusted, so access-control-allow-origin must not be returned
    assert response.headers.get("access-control-allow-origin") is None


def test_cors_arbitrary_vercel_origin_rejected(client):
    response = client.options(
        "/api/health",
        headers={
            "Origin": "https://arbitrary-attacker.vercel.app",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") is None

