import json
from typing import Any

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.infrastructure.openrouter import get_openrouter_client
from src.tools.english_tools import ENGLISH_TOOLS, execute_english_tool
from src.tools.vault_tools import VAULT_TOOLS
from src.tools.vault_tools import execute_tool as execute_vault_tool

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
    usage: dict[str, Any] | None = None
    tools_used: list[str] | None = None


# Combine all tools
ALL_TOOLS = VAULT_TOOLS + ENGLISH_TOOLS

# Tool name to executor mapping
ENGLISH_TOOL_NAMES = {tool["name"] for tool in ENGLISH_TOOLS}


async def execute_tool(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Route tool execution to the appropriate handler."""
    if tool_name in ENGLISH_TOOL_NAMES:
        return await execute_english_tool(tool_name, tool_input)
    return await execute_vault_tool(tool_name, tool_input)


SYSTEM_PROMPT = """You are Dave, a friendly AI assistant.
You help with productivity and English learning.

Key traits:
- Friendly and encouraging, but not overly enthusiastic
- You help organize tasks, notes, and daily activities
- You actively help improve the user's English
- You communicate in the user's preferred language (Spanish or English)
- You're concise and practical

OBSIDIAN VAULT ACCESS:
You have access to the user's Obsidian vault (PARA method):
- Read/create notes, daily notes, search the vault
- Add items to daily note sections (quick_capture, notes, tasks, gastos)

ENGLISH CORRECTION (Important!):
When the user writes in English and makes a mistake:
1. First respond to their message naturally
2. Then add a correction using this format:
   📝 **English tip:** [brief explanation]
   ❌ "[incorrect]" → ✅ "[correct]"
3. Use log_english_correction to save significant errors
4. Focus on errors that matter - don't correct everything
5. Categories: grammar, vocabulary, spelling, expression

The user is a Spanish speaker learning English. Watch for:
- Verb tense errors (especially present perfect vs simple past)
- Article usage (a/an/the or missing articles)
- Preposition errors (common Spanish-English differences)
- False friends and literal translations
- Word order issues"""


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Send a message to Dave and get a response."""
    try:
        client = get_openrouter_client()
        tools_used: list[str] = []

        # Prepare messages with system prompt
        messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend([{"role": m.role, "content": m.content} for m in request.messages])

        # Tool execution loop
        for _ in range(MAX_TOOL_ITERATIONS):
            response = await client.chat(
                messages=messages,
                model=request.model,
                tools=ALL_TOOLS,
            )

            assistant_message = response["choices"][0]["message"]

            # Check if the model wants to use a tool
            if "tool_calls" in assistant_message and assistant_message["tool_calls"]:
                # Clean assistant message - only include required fields
                clean_tool_calls: list[dict[str, Any]] = []
                for tc in assistant_message["tool_calls"]:
                    clean_tc: dict[str, Any] = {
                        "id": tc.get("id", f"call_{tc['function']['name']}"),
                        "type": "function",
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": tc["function"].get("arguments", "{}"),
                        },
                    }
                    clean_tool_calls.append(clean_tc)

                clean_assistant_msg: dict[str, Any] = {
                    "role": "assistant",
                    "content": assistant_message.get("content", ""),
                    "tool_calls": clean_tool_calls,
                }
                messages.append(clean_assistant_msg)

                # Execute each tool call
                for tool_call in clean_tool_calls:
                    tool_name = str(tool_call["function"]["name"])
                    args_str = str(tool_call["function"]["arguments"])
                    tool_input: dict[str, Any] = json.loads(args_str) if args_str else {}

                    logger.info("tool_execution", tool=tool_name, input=tool_input)
                    tools_used.append(tool_name)

                    # Execute the tool
                    result = await execute_tool(tool_name, tool_input)

                    # Truncate very long results to avoid API limits
                    if len(result) > 10000:
                        result = result[:10000] + "\n\n[Content truncated...]"

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
                    model=str(response.get("model", "unknown")),
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
