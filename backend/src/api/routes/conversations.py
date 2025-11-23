"""API routes for conversation management."""

import json
from typing import Any

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.core.conversation_service import (
    create_conversation,
    get_conversation,
    get_conversations_grouped,
    add_message,
    update_conversation_title,
    delete_conversation,
    generate_title_from_message,
)

logger = structlog.get_logger()
router = APIRouter(tags=["conversations"])


class MessageSchema(BaseModel):
    """Schema for a message."""
    role: str
    content: str


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    title: str | None = None
    messages: list[MessageSchema] | None = None


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    title: str


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    id: str
    title: str | None
    created_at: str
    updated_at: str
    messages: list[dict[str, Any]]


class ConversationListItem(BaseModel):
    """Schema for conversation list item."""
    id: str
    title: str
    updated_at: str


class GroupedConversationsResponse(BaseModel):
    """Schema for grouped conversations response."""
    groups: dict[str, list[ConversationListItem]]


@router.post("/conversations", response_model=ConversationResponse)
async def create_new_conversation(request: ConversationCreate) -> ConversationResponse:
    """Create a new conversation."""
    conversation = await create_conversation(request.title)

    if not conversation:
        raise HTTPException(status_code=500, detail="Failed to create conversation")

    # If initial messages provided, add them
    messages_data = []
    if request.messages:
        for msg in request.messages:
            message = await add_message(
                conversation_id=conversation.id,
                role=msg.role,
                content=msg.content,
            )
            if message:
                messages_data.append({
                    "id": message.id,
                    "role": message.role,
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                })

        # Auto-generate title from first user message if not provided
        if not request.title and request.messages:
            first_user_msg = next((m for m in request.messages if m.role == "user"), None)
            if first_user_msg:
                title = await generate_title_from_message(first_user_msg.content)
                await update_conversation_title(conversation.id, title)
                conversation.title = title

    logger.info("conversation_created_via_api", id=conversation.id)

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
        messages=messages_data,
    )


@router.get("/conversations", response_model=GroupedConversationsResponse)
async def list_conversations() -> GroupedConversationsResponse:
    """Get all conversations grouped by time period."""
    groups = await get_conversations_grouped()
    return GroupedConversationsResponse(groups=groups)


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_by_id(conversation_id: str) -> ConversationResponse:
    """Get a conversation with all its messages."""
    conversation = await get_conversation(conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages_data = [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
            "model": msg.model,
            "tools_used": json.loads(msg.tools_used) if msg.tools_used else None,
        }
        for msg in conversation.messages
    ]

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
        messages=messages_data,
    )


@router.patch("/conversations/{conversation_id}")
async def update_conversation(conversation_id: str, request: ConversationUpdate) -> dict[str, str]:
    """Update a conversation's title."""
    success = await update_conversation_title(conversation_id, request.title)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update conversation")

    return {"status": "updated", "id": conversation_id}


@router.delete("/conversations/{conversation_id}")
async def delete_conversation_by_id(conversation_id: str) -> dict[str, str]:
    """Delete a conversation."""
    success = await delete_conversation(conversation_id)

    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"status": "deleted", "id": conversation_id}


@router.post("/conversations/{conversation_id}/messages")
async def add_message_to_conversation(
    conversation_id: str,
    request: MessageSchema,
) -> dict[str, Any]:
    """Add a message to an existing conversation."""
    message = await add_message(
        conversation_id=conversation_id,
        role=request.role,
        content=request.content,
    )

    if not message:
        raise HTTPException(status_code=500, detail="Failed to add message")

    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at.isoformat(),
    }
