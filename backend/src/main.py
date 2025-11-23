import structlog

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import auth, chat, conversations, documents, english, health, rag, vault
from src.config import get_settings
from src.infrastructure.database import init_db
from src.infrastructure.embeddings import get_embedding_service
from src.infrastructure.vector_store.qdrant_client import (
    get_qdrant_client,
    init_qdrant_collections,
)
from src.infrastructure.vector_store.uploaded_document_repository import (
    get_uploaded_document_repository,
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="Your AI friend for productivity and English learning",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://localhost:5176",
        ],  # Vite dev server ports
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix=settings.api_prefix)
    app.include_router(chat.router, prefix=settings.api_prefix)
    app.include_router(conversations.router, prefix=settings.api_prefix)
    app.include_router(vault.router, prefix=settings.api_prefix)
    app.include_router(auth.router, prefix=settings.api_prefix)
    app.include_router(english.router, prefix=settings.api_prefix)
    app.include_router(rag.router, prefix=settings.api_prefix)
    app.include_router(documents.router, prefix=settings.api_prefix)

    @app.on_event("startup")
    async def startup_event() -> None:
        # Initialize database tables
        await init_db()

        # Initialize Qdrant collections
        try:
            await init_qdrant_collections()
            # Initialize uploaded documents collections
            doc_repo = get_uploaded_document_repository()
            await doc_repo.ensure_collections()
            logger.info("qdrant_initialized")
        except Exception as e:
            logger.warning("qdrant_init_failed", error=str(e))

        logger.info("application_started", app_name=settings.app_name)

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        # Close Qdrant client
        try:
            qdrant = get_qdrant_client()
            await qdrant.close()
        except Exception:
            pass

        # Close embedding service
        try:
            embedding_service = get_embedding_service()
            await embedding_service.close()
        except Exception:
            pass

        logger.info("application_shutdown")

    return app


app = create_app()
