import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.infrastructure.openrouter import get_openrouter_client

logger = structlog.get_logger()
router = APIRouter(tags=["chat"])


class Message(BaseModel):
    """A chat message."""

    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    messages: list[Message]
    model: str | None = None


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    message: Message
    model: str
    usage: dict | None = None


SYSTEM_PROMPT = """You are Dave, a friendly AI assistant.
You help with productivity and English learning.

Key traits:
- Friendly and encouraging, but not overly enthusiastic
- You help organize tasks, notes, and daily activities
- You gently correct English mistakes and explain improvements
- You communicate in the user's preferred language (Spanish or English)
- You're concise and practical

When correcting English:
- Point out the mistake kindly
- Explain why it's wrong
- Give the correct version
- Provide a simple example if helpful"""


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Send a message to Dave and get a response."""
    try:
        client = get_openrouter_client()

        # Prepare messages with system prompt
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend([{"role": m.role, "content": m.content} for m in request.messages])

        # Get response from OpenRouter
        response = await client.chat(messages=messages, model=request.model)

        # Extract assistant message
        assistant_message = response["choices"][0]["message"]

        logger.info(
            "chat_response_sent",
            model=response.get("model"),
            usage=response.get("usage"),
        )

        return ChatResponse(
            message=Message(
                role=assistant_message["role"],
                content=assistant_message["content"],
            ),
            model=response.get("model", "unknown"),
            usage=response.get("usage"),
        )

    except Exception as e:
        logger.error("chat_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
