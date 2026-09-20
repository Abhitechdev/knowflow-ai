import pytest
from app.main import app
from starlette.testclient import TestClient


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
