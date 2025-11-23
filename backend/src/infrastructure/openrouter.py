import json
from collections.abc import AsyncIterator
from typing import Any

import httpx
import structlog

from src.config import get_settings

logger = structlog.get_logger()


class OpenRouterClient:
    """Client for OpenRouter API."""

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.openrouter_api_key
        self.base_url = settings.openrouter_base_url
        self.default_model = settings.default_model

    def _get_headers(self) -> dict[str, str]:
        """Get common headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/YoSoyDavidB/dave",
            "X-Title": "Dave AI Assistant",
        }

    def _build_payload(
        self,
        messages: list[dict[str, Any]],
        model: str,
        stream: bool = False,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Build the request payload."""
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }

        if tools:
            payload["tools"] = [
                {"type": "function", "function": tool} for tool in tools
            ]

        return payload

    async def chat(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        stream: bool = False,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Send a chat completion request to OpenRouter (non-streaming)."""
        model = model or self.default_model
        headers = self._get_headers()
        payload = self._build_payload(messages, model, stream=False, tools=tools)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            logger.info(
                "chat_completion",
                model=model,
                tokens=data.get("usage", {}),
            )
            return data

    async def chat_stream(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Stream chat completion from OpenRouter.

        Yields chunks with structure:
        - {"type": "content", "content": "text"} for text chunks
        - {"type": "tool_call", "tool_calls": [...]} for tool calls
        - {"type": "done", "usage": {...}} when complete
        - {"type": "error", "error": "message"} on error
        """
        model = model or self.default_model
        headers = self._get_headers()
        payload = self._build_payload(messages, model, stream=True, tools=tools)

        logger.info("chat_stream_start", model=model)

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=120.0,
                ) as response:
                    response.raise_for_status()

                    accumulated_content = ""
                    accumulated_tool_calls: list[dict[str, Any]] = []
                    current_tool_call: dict[str, Any] | None = None

                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue

                        data_str = line[6:]  # Remove "data: " prefix

                        if data_str == "[DONE]":
                            # Stream complete
                            if accumulated_tool_calls:
                                yield {
                                    "type": "tool_call",
                                    "tool_calls": accumulated_tool_calls,
                                }
                            yield {"type": "done", "content": accumulated_content}
                            break

                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})

                            # Handle text content
                            if "content" in delta and delta["content"]:
                                content = delta["content"]
                                accumulated_content += content
                                yield {"type": "content", "content": content}

                            # Handle tool calls (streaming)
                            if "tool_calls" in delta:
                                for tc_delta in delta["tool_calls"]:
                                    tc_index = tc_delta.get("index", 0)

                                    # Ensure we have enough slots
                                    while len(accumulated_tool_calls) <= tc_index:
                                        accumulated_tool_calls.append({
                                            "id": "",
                                            "type": "function",
                                            "function": {"name": "", "arguments": ""},
                                        })

                                    tc = accumulated_tool_calls[tc_index]

                                    if "id" in tc_delta:
                                        tc["id"] = tc_delta["id"]

                                    if "function" in tc_delta:
                                        func = tc_delta["function"]
                                        if "name" in func:
                                            tc["function"]["name"] = func["name"]
                                        if "arguments" in func:
                                            tc["function"]["arguments"] += func["arguments"]

                            # Check finish reason
                            finish_reason = chunk.get("choices", [{}])[0].get("finish_reason")
                            if finish_reason == "tool_calls" and accumulated_tool_calls:
                                yield {
                                    "type": "tool_call",
                                    "tool_calls": accumulated_tool_calls,
                                }

                            # Capture usage if present (usually in last chunk)
                            if "usage" in chunk:
                                logger.info(
                                    "chat_stream_complete",
                                    model=model,
                                    tokens=chunk["usage"],
                                )

                        except json.JSONDecodeError as e:
                            logger.warning("stream_parse_error", error=str(e), line=data_str)
                            continue

        except httpx.HTTPStatusError as e:
            logger.error("stream_http_error", status=e.response.status_code, error=str(e))
            yield {"type": "error", "error": f"HTTP error: {e.response.status_code}"}
        except httpx.RequestError as e:
            logger.error("stream_request_error", error=str(e))
            yield {"type": "error", "error": f"Request error: {str(e)}"}
        except Exception as e:
            logger.error("stream_error", error=str(e))
            yield {"type": "error", "error": str(e)}


def get_openrouter_client() -> OpenRouterClient:
    """Get OpenRouter client instance."""
    return OpenRouterClient()
