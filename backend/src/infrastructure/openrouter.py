from collections.abc import AsyncIterator

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

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        stream: bool = False,
    ) -> dict | AsyncIterator[str]:
        """Send a chat completion request to OpenRouter."""
        model = model or self.default_model

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/YoSoyDavidB/dave",
            "X-Title": "Dave AI Assistant",
        }

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }

        async with httpx.AsyncClient() as client:
            if stream:
                return self._stream_response(client, headers, payload)
            else:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()
                logger.info(
                    "chat_completion",
                    model=model,
                    tokens=data.get("usage", {}),
                )
                return data

    async def _stream_response(
        self,
        client: httpx.AsyncClient,
        headers: dict,
        payload: dict,
    ) -> AsyncIterator[str]:
        """Stream response chunks from OpenRouter."""
        async with client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60.0,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk != "[DONE]":
                        yield chunk


def get_openrouter_client() -> OpenRouterClient:
    """Get OpenRouter client instance."""
    return OpenRouterClient()
