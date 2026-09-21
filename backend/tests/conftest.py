import pytest
import asyncio
from app.main import app
from starlette.testclient import TestClient
from app.db.session import get_engine
from app.models import Base

from sqlalchemy import text

@pytest.fixture(autouse=True, scope="session")
def setup_test_db():
    engine = get_engine()
    if engine is not None:
        async def init_db():
            async with engine.begin() as conn:
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                except Exception:
                    pass
                await conn.run_sync(Base.metadata.create_all)
                # Seed default workspace and user if needed
                check_ws = await conn.execute(text("SELECT id FROM workspaces WHERE id = 'ws-default-001'"))
                if not check_ws.scalar_one_or_none():
                    await conn.execute(text(
                        "INSERT INTO workspaces (id, name, slug, created_at, updated_at) "
                        "VALUES ('ws-default-001', 'Acme Pharma — DEMO COMPANY', 'acme-pharma', NOW(), NOW())"
                    ))
                check_user = await conn.execute(text("SELECT id FROM users WHERE id = 'usr-admin-001'"))
                if not check_user.scalar_one_or_none():
                    await conn.execute(text(
                        "INSERT INTO users (id, email, full_name, role, is_active, created_at, updated_at) "
                        "VALUES ('usr-admin-001', 'compliance@acmepharma.demo', 'Compliance Lead', 'ADMIN', true, NOW(), NOW())"
                    ))
                check_mem = await conn.execute(text("SELECT id FROM workspace_members WHERE id = 'mem-default-001'"))
                if not check_mem.scalar_one_or_none():
                    await conn.execute(text(
                        "INSERT INTO workspace_members (id, workspace_id, user_id, role, joined_at) "
                        "VALUES ('mem-default-001', 'ws-default-001', 'usr-admin-001', 'ADMIN', NOW())"
                    ))
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
