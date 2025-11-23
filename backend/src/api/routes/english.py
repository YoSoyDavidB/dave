from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from src.api.routes.auth import get_current_user
from src.core.english_service import (
    get_corrections_by_category,
    get_error_stats,
    get_recent_corrections,
)
from src.core.models import User

router = APIRouter(prefix="/english", tags=["english"])


class CorrectionResponse(BaseModel):
    id: int
    created_at: str
    original_text: str
    corrected_text: str
    explanation: str
    category: str
    subcategory: str | None
    conversation_context: str | None

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total_corrections: int
    by_category: dict[str, int]
    last_7_days: int


@router.get("/corrections", response_model=list[CorrectionResponse])
async def get_corrections(
    current_user: Annotated[User, Depends(get_current_user)],
    days: int = Query(default=7, ge=1, le=365),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Get recent English corrections."""
    corrections = await get_recent_corrections(days=days, limit=limit)
    return [
        CorrectionResponse(
            id=c.id,
            created_at=c.created_at.isoformat(),
            original_text=c.original_text,
            corrected_text=c.corrected_text,
            explanation=c.explanation,
            category=c.category,
            subcategory=c.subcategory,
            conversation_context=c.conversation_context,
        )
        for c in corrections
    ]


@router.get("/corrections/category/{category}", response_model=list[CorrectionResponse])
async def get_corrections_for_category(
    category: str,
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(default=20, ge=1, le=100),
):
    """Get English corrections by category."""
    corrections = await get_corrections_by_category(category=category, limit=limit)
    return [
        CorrectionResponse(
            id=c.id,
            created_at=c.created_at.isoformat(),
            original_text=c.original_text,
            corrected_text=c.corrected_text,
            explanation=c.explanation,
            category=c.category,
            subcategory=c.subcategory,
            conversation_context=c.conversation_context,
        )
        for c in corrections
    ]


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get English learning statistics."""
    stats = await get_error_stats()
    return StatsResponse(**stats)
