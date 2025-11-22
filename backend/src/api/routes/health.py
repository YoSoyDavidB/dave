from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: datetime
    version: str


class DetailedHealthResponse(BaseModel):
    """Detailed health check response with service status."""

    status: str
    timestamp: datetime
    version: str
    services: dict[str, dict[str, str]]


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="0.1.0"
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check() -> DetailedHealthResponse:
    """
    Detailed health check with service status.
    TODO: Implement actual service checks.
    """
    return DetailedHealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="0.1.0",
        services={
            "llm": {"status": "not_configured"},
            "github": {"status": "not_configured"},
            "qdrant": {"status": "not_configured"},
            "neo4j": {"status": "not_configured"},
            "redis": {"status": "not_configured"},
        }
    )
