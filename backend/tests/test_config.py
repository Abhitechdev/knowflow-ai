from app.core.config import Settings


def test_default_settings():
    s = Settings()
    assert s.PROJECT_NAME == "KnowFlow AI"
    assert s.PORT == 8000
    assert len(s.CORS_ORIGINS) >= 2


def test_cors_origins_parsing():
    s = Settings(CORS_ORIGINS='["http://example.com", "http://app.local"]')
    assert "http://example.com" in s.CORS_ORIGINS
    assert "http://app.local" in s.CORS_ORIGINS
