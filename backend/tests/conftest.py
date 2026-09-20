import pytest
import asyncio
from app.main import app
from starlette.testclient import TestClient
from app.db.session import get_engine
from app.models import Base

@pytest.fixture(autouse=True, scope="session")
def setup_test_db():
    engine = get_engine()
    if engine is not None:
        async def init_db():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        # Run initialization
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # In case it's somehow running, we create task
            loop.create_task(init_db())
        else:
            loop.run_until_complete(init_db())

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
