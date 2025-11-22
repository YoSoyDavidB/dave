from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_chat_endpoint_success(client: TestClient) -> None:
    """Test successful chat completion."""
    mock_response = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Hello! How can I help you today?",
                }
            }
        ],
        "model": "anthropic/claude-3-sonnet",
        "usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18},
    }

    with patch(
        "src.api.routes.chat.get_openrouter_client"
    ) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.chat.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/v1/chat",
            json={"messages": [{"role": "user", "content": "Hi Dave!"}]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"]["role"] == "assistant"
        assert data["message"]["content"] == "Hello! How can I help you today?"
        assert data["model"] == "anthropic/claude-3-sonnet"


def test_chat_endpoint_with_history(client: TestClient) -> None:
    """Test chat with conversation history."""
    mock_response = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Your name is David!",
                }
            }
        ],
        "model": "anthropic/claude-3-sonnet",
        "usage": {"prompt_tokens": 20, "completion_tokens": 5, "total_tokens": 25},
    }

    with patch(
        "src.api.routes.chat.get_openrouter_client"
    ) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.chat.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/v1/chat",
            json={
                "messages": [
                    {"role": "user", "content": "My name is David"},
                    {"role": "assistant", "content": "Nice to meet you, David!"},
                    {"role": "user", "content": "What's my name?"},
                ]
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"]["content"] == "Your name is David!"


def test_chat_endpoint_error(client: TestClient) -> None:
    """Test chat error handling."""
    with patch(
        "src.api.routes.chat.get_openrouter_client"
    ) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.chat.side_effect = Exception("API error")
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/v1/chat",
            json={"messages": [{"role": "user", "content": "Hi"}]},
        )

        assert response.status_code == 500
        assert "Chat error" in response.json()["detail"]
