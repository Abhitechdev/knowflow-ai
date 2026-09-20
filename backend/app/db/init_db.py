import asyncio
import logging
from sqlalchemy import text
from app.db.base import Base
from app.db.session import get_engine
import app.models  # Ensure all models are registered

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_db")


async def init_db():
    engine = get_engine()
    if engine is None:
        raise RuntimeError("Database engine not available. Check DATABASE_URL.")

    logger.info("Connecting to database and initializing schema...")

    async with engine.begin() as conn:
        # 1. Enable pgvector extension
        logger.info("Enabling pgvector extension...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        # 2. Create all registered tables
        logger.info("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)

        # 3. Create HNSW index for vector cosine similarity retrieval
        logger.info("Creating HNSW vector index on document_chunks...")
        try:
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding "
                "ON document_chunks USING hnsw (embedding vector_cosine_ops);"
            ))
        except Exception as exc:
            logger.warning(f"Note on HNSW index: {exc}")

        # 4. Seed default workspace and admin user if not present
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

    logger.info("Database schema initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
