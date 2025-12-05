from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import get_settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


settings = get_settings()

# Convert DATABASE_URL format if needed (postgresql:// -> postgresql+asyncpg://)
db_url = settings.database_url
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(db_url, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session() as session:
        yield session


async def init_db() -> None:
    """Initialize database tables."""
    import structlog

    logger = structlog.get_logger()

    # Import models to register them with SQLAlchemy
    from src.core.models import (  # noqa: F401
        Conversation,
        DailySummaryModel,
        EnglishCorrection,
        FocusSessionModel,
        Message,
        User,
    )

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("database_initialized")
    except Exception as e:
        logger.warning("database_init_failed", error=str(e))
        # Don't fail startup - database features will be unavailable
