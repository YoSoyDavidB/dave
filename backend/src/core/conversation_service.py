"""Service for managing chat conversations."""

import json
from datetime import datetime, timedelta
from typing import Any

import structlog
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from src.core.models import Conversation, Message
from src.infrastructure.database import async_session

logger = structlog.get_logger()


async def create_conversation(title: str | None = None) -> Conversation | None:
    """Create a new conversation."""
    try:
        async with async_session() as session:
            conversation = Conversation(title=title)
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
            logger.info("conversation_created", id=conversation.id)
            return conversation
    except Exception as e:
        logger.error("failed_to_create_conversation", error=str(e))
        return None


async def get_conversation(conversation_id: str) -> Conversation | None:
    """Get a conversation by ID with all its messages."""
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Conversation)
                .where(Conversation.id == conversation_id)
                .options(selectinload(Conversation.messages))
            )
            return result.scalar_one_or_none()
    except Exception as e:
        logger.error("failed_to_get_conversation", id=conversation_id, error=str(e))
        return None


async def get_recent_conversations(limit: int = 20) -> list[Conversation]:
    """Get recent conversations ordered by last update."""
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Conversation).order_by(Conversation.updated_at.desc()).limit(limit)
            )
            return list(result.scalars().all())
    except Exception as e:
        logger.error("failed_to_get_recent_conversations", error=str(e))
        return []


async def get_conversations_grouped() -> dict[str, list[dict[str, Any]]]:
    """Get conversations grouped by time period for sidebar display."""
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Conversation).order_by(Conversation.updated_at.desc()).limit(50)
            )
            conversations = list(result.scalars().all())

            now = datetime.utcnow()
            today = now.date()
            yesterday = today - timedelta(days=1)
            week_ago = today - timedelta(days=7)

            groups: dict[str, list[dict[str, Any]]] = {
                "Today": [],
                "Yesterday": [],
                "This Week": [],
                "Older": [],
            }

            for conv in conversations:
                conv_date = conv.updated_at.date()
                conv_dict = {
                    "id": conv.id,
                    "title": conv.title or "New conversation",
                    "updated_at": conv.updated_at.isoformat(),
                }

                if conv_date == today:
                    groups["Today"].append(conv_dict)
                elif conv_date == yesterday:
                    groups["Yesterday"].append(conv_dict)
                elif conv_date > week_ago:
                    groups["This Week"].append(conv_dict)
                else:
                    groups["Older"].append(conv_dict)

            # Remove empty groups
            return {k: v for k, v in groups.items() if v}

    except Exception as e:
        logger.error("failed_to_get_grouped_conversations", error=str(e))
        return {}


async def add_message(
    conversation_id: str,
    role: str,
    content: str,
    model: str | None = None,
    tools_used: list[str] | None = None,
) -> Message | None:
    """Add a message to a conversation."""
    try:
        async with async_session() as session:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                model=model,
                tools_used=json.dumps(tools_used) if tools_used else None,
            )
            session.add(message)

            # Update conversation's updated_at
            await session.execute(
                update(Conversation)
                .where(Conversation.id == conversation_id)
                .values(updated_at=datetime.utcnow())
            )

            await session.commit()
            await session.refresh(message)
            return message
    except Exception as e:
        logger.error("failed_to_add_message", conversation_id=conversation_id, error=str(e))
        return None


async def update_conversation_title(conversation_id: str, title: str) -> bool:
    """Update a conversation's title."""
    try:
        async with async_session() as session:
            await session.execute(
                update(Conversation)
                .where(Conversation.id == conversation_id)
                .values(title=title[:255])  # Truncate to max length
            )
            await session.commit()
            return True
    except Exception as e:
        logger.error("failed_to_update_title", conversation_id=conversation_id, error=str(e))
        return False


async def delete_conversation(conversation_id: str) -> bool:
    """Delete a conversation and all its messages."""
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()

            if conversation:
                await session.delete(conversation)
                await session.commit()
                logger.info("conversation_deleted", id=conversation_id)
                return True
            return False
    except Exception as e:
        logger.error("failed_to_delete_conversation", conversation_id=conversation_id, error=str(e))
        return False


async def generate_title_from_message(content: str) -> str:
    """Generate a short title from the first message content."""
    # Take first 50 chars and truncate at last space if needed
    title = content[:50].strip()
    if len(content) > 50:
        last_space = title.rfind(" ")
        if last_space > 20:
            title = title[:last_space]
        title += "..."
    return title
