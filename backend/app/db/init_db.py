import asyncio
import logging
import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from app.db.session import get_engine
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_db")


def run_alembic_upgrade():
    """Run alembic upgrade head programmatically."""
    backend_dir = Path(__file__).resolve().parent.parent.parent
    ini_path = backend_dir / "alembic.ini"
    alembic_dir = backend_dir / "alembic"
    
    logger.info("Applying Alembic migrations to head...")
    cfg = Config(str(ini_path))
    cfg.set_main_option("script_location", str(alembic_dir))
    command.upgrade(cfg, "head")
    logger.info("Alembic migrations applied successfully.")


async def seed_default_data():
    """Seed demo/default workspace and admin user if needed."""
    engine = get_engine()
    if engine is None:
        raise RuntimeError("Database engine not available. Check DATABASE_URL.")

    async with engine.begin() as conn:
        logger.info("Verifying default demo workspace and admin user...")
        check_ws = await conn.execute(
            text("SELECT id FROM workspaces WHERE id = 'ws-default-001'")
        )
        if not check_ws.scalar_one_or_none():
            await conn.execute(text(
                "INSERT INTO workspaces (id, name, slug, created_at, updated_at) "
                "VALUES ('ws-default-001', 'Acme Pharma — DEMO COMPANY', 'acme-pharma', NOW(), NOW())"
            ))
            logger.info("Seeded default workspace: Acme Pharma — DEMO COMPANY")

        check_user = await conn.execute(
            text("SELECT id FROM users WHERE id = 'usr-admin-001'")
        )
        if not check_user.scalar_one_or_none():
            await conn.execute(text(
                "INSERT INTO users (id, email, full_name, role, is_active, created_at, updated_at) "
                "VALUES ('usr-admin-001', 'compliance@acmepharma.demo', 'Compliance Lead', 'ADMIN', true, NOW(), NOW())"
            ))
            logger.info("Seeded default admin: Compliance Lead")


def init_db():
    run_alembic_upgrade()
    asyncio.run(seed_default_data())


if __name__ == "__main__":
    init_db()

