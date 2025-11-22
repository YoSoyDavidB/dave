from typing import Any

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.infrastructure.github_vault import get_github_vault_client

logger = structlog.get_logger()
router = APIRouter(tags=["vault"])


class FileContent(BaseModel):
    """File content response."""

    path: str
    content: str
    sha: str | None = None


class FileCreate(BaseModel):
    """Request to create a file."""

    path: str
    content: str
    message: str | None = None


class FileUpdate(BaseModel):
    """Request to update a file."""

    content: str
    sha: str
    message: str | None = None


class DirectoryItem(BaseModel):
    """Directory item."""

    name: str
    path: str
    type: str  # "file" or "dir"


class SearchResult(BaseModel):
    """Search result item."""

    name: str
    path: str


@router.get("/vault/file", response_model=FileContent | None)
async def get_file(path: str) -> FileContent | None:
    """Get a file from the vault."""
    try:
        client = get_github_vault_client()
        result = await client.get_file(path)

        if result is None:
            raise HTTPException(status_code=404, detail=f"File not found: {path}")

        return FileContent(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("vault_get_file_error", path=path, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vault/file", response_model=dict[str, str])
async def create_file(request: FileCreate) -> dict[str, str]:
    """Create a new file in the vault."""
    try:
        client = get_github_vault_client()

        # Check if file already exists
        existing = await client.get_file(request.path)
        if existing is not None:
            raise HTTPException(
                status_code=409,
                detail=f"File already exists: {request.path}"
            )

        await client.create_file(
            path=request.path,
            content=request.content,
            message=request.message,
        )

        return {"status": "created", "path": request.path}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("vault_create_file_error", path=request.path, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/vault/file", response_model=dict[str, str])
async def update_file(path: str, request: FileUpdate) -> dict[str, str]:
    """Update an existing file in the vault."""
    try:
        client = get_github_vault_client()

        await client.update_file(
            path=path,
            content=request.content,
            sha=request.sha,
            message=request.message,
        )

        return {"status": "updated", "path": path}

    except Exception as e:
        logger.error("vault_update_file_error", path=path, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vault/directory", response_model=list[DirectoryItem])
async def list_directory(path: str = "") -> list[DirectoryItem]:
    """List files in a vault directory."""
    try:
        client = get_github_vault_client()
        items = await client.list_directory(path)
        return [DirectoryItem(**item) for item in items]

    except Exception as e:
        logger.error("vault_list_error", path=path, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vault/search", response_model=list[SearchResult])
async def search_vault(query: str) -> list[SearchResult]:
    """Search for files in the vault."""
    try:
        client = get_github_vault_client()
        results = await client.search_files(query)
        return [SearchResult(**item) for item in results]

    except Exception as e:
        logger.error("vault_search_error", query=query, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vault/daily-note", response_model=FileContent | None)
async def get_daily_note() -> FileContent | None:
    """Get today's daily note."""
    try:
        client = get_github_vault_client()
        path = await client.get_daily_note_path()
        result = await client.get_file(path)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Daily note not found: {path}"
            )

        return FileContent(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("vault_daily_note_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
