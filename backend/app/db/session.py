import logging
from collections.abc import AsyncGenerator
from typing import Any

from app.core.config import settings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger(__name__)

# Global engine and session factory
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine | None:
    """Returns async SQLAlchemy engine if DATABASE_URL is configured."""
    global _engine, _session_factory
    if _engine is not None:
        return _engine

    url = settings.DATABASE_URL.strip()
    if not url:
        return None

    # Normalise standard postgresql:// to postgresql+asyncpg:// if needed
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)

    connect_args = {}
    if url.startswith("postgresql"):
        import uuid
        connect_args["statement_cache_size"] = 0
        connect_args["prepared_statement_cache_size"] = 0
        connect_args["prepared_statement_name_func"] = lambda: f"__asyncpg_{uuid.uuid4().hex}__"

    try:
        if url.startswith("sqlite"):
            from sqlalchemy.pool import StaticPool
            poolclass = StaticPool
            connect_args["check_same_thread"] = False
        else:
            from sqlalchemy.pool import NullPool
            poolclass = NullPool

        _engine = create_async_engine(
            url,
            poolclass=poolclass,
            echo=False,
            connect_args=connect_args,
        )
        _session_factory = async_sessionmaker(
            bind=_engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        logger.info("Database engine initialized successfully.")
        return _engine
    except Exception as exc:
        logger.error(f"Failed to create database engine: {exc}")
        return None


def get_session_factory() -> async_sessionmaker[AsyncSession] | None:
    """Returns the async sessionmaker factory."""
    get_engine()
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for DB sessions. Raises RuntimeError if DB is unconfigured."""
    engine = get_engine()
    if engine is None or _session_factory is None:
        raise RuntimeError("Database is not configured. Set DATABASE_URL in .env")
    async with _session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def check_database_health() -> dict[str, Any]:
    """Checks DB connectivity without crashing if unconfigured."""
    if not settings.DATABASE_URL.strip():
        return {
            "status": "unconfigured",
            "connected": False,
            "message": "DATABASE_URL is not set. Local development mode active.",
        }

    engine = get_engine()
    if engine is None:
        return {
            "status": "error",
            "connected": False,
            "message": "Failed to initialize database engine.",
        }

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "connected": True,
            "message": "Database connection verified.",
        }
    except Exception as exc:
        logger.warning(f"Database health probe failed: {exc}")
        return {
            "status": "disconnected",
            "connected": False,
            "message": str(exc),
        }
