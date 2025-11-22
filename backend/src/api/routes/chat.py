import json

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.infrastructure.openrouter import get_openrouter_client
from src.tools.vault_tools import VAULT_TOOLS, execute_tool

logger = structlog.get_logger()
router = APIRouter(tags=["chat"])

MAX_TOOL_ITERATIONS = 5


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
    tools_used: list[str] | None = None


SYSTEM_PROMPT = """You are Dave, a friendly AI assistant.
You help with productivity and English learning.

Key traits:
- Friendly and encouraging, but not overly enthusiastic
- You help organize tasks, notes, and daily activities
- You gently correct English mistakes and explain improvements
- You communicate in the user's preferred language (Spanish or English)
- You're concise and practical

You have access to the user's Obsidian vault. Use the tools to:
- Read their daily notes to understand context
- Create new notes to help organize their thoughts
- Search for relevant information in their vault
- Add items to their daily note (quick capture, tasks, expenses)

The vault follows the PARA method:
- Inbox: Quick capture and unprocessed notes
- Project: Active projects with deadlines
- Area: Ongoing responsibilities (Terapia, English, etc.)
- Resource: Reference materials
- Timestamps: Daily notes organized by year/month

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
        tools_used: list[str] = []

        # Prepare messages with system prompt
        messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend([{"role": m.role, "content": m.content} for m in request.messages])

        # Tool execution loop
        for iteration in range(MAX_TOOL_ITERATIONS):
            response = await client.chat(
                messages=messages,
                model=request.model,
                tools=VAULT_TOOLS,
            )

            assistant_message = response["choices"][0]["message"]

            # Check if the model wants to use a tool
            if "tool_calls" in assistant_message and assistant_message["tool_calls"]:
                # Add assistant message with tool calls
                messages.append(assistant_message)

                # Execute each tool call
                for tool_call in assistant_message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    tool_input = json.loads(tool_call["function"]["arguments"])

                    logger.info("tool_execution", tool=tool_name, input=tool_input)
                    tools_used.append(tool_name)

                    # Execute the tool
                    result = await execute_tool(tool_name, tool_input)

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result,
                    })
            else:
                # No more tool calls, return the response
                logger.info(
                    "chat_response_sent",
                    model=response.get("model"),
                    usage=response.get("usage"),
                    tools_used=tools_used,
                )

                return ChatResponse(
                    message=Message(
                        role="assistant",
                        content=assistant_message.get("content", ""),
                    ),
                    model=response.get("model", "unknown"),
                    usage=response.get("usage"),
                    tools_used=tools_used if tools_used else None,
                )

        # Max iterations reached
        return ChatResponse(
            message=Message(
                role="assistant",
                content="I apologize, but I'm having trouble completing this request.",
            ),
            model="unknown",
            tools_used=tools_used if tools_used else None,
        )

    except Exception as e:
        logger.error("chat_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
