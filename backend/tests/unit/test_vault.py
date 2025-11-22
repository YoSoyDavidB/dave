from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_get_file_success(client: TestClient) -> None:
    """Test getting a file from vault."""
    mock_file = {
        "content": "# Test Note\n\nThis is a test.",
        "sha": "abc123",
        "path": "test.md",
    }

    with patch(
        "src.api.routes.vault.get_github_vault_client"
    ) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.get_file.return_value = mock_file
        mock_get_client.return_value = mock_client

        response = client.get("/api/v1/vault/file", params={"path": "test.md"})

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "# Test Note\n\nThis is a test."
        assert data["sha"] == "abc123"


def test_get_file_not_found(client: TestClient) -> None:
    """Test getting a non-existent file."""
    with patch(
        "src.api.routes.vault.get_github_vault_client"
    ) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.get_file.return_value = None
        mock_get_client.return_value = mock_client

        response = client.get(
            "/api/v1/vault/file",
            params={"path": "nonexistent.md"}
        )

        assert response.status_code == 404


def test_create_file_success(client: TestClient) -> None:
    """Test creating a new file."""
    with patch(
        "src.api.routes.vault.get_github_vault_client"
    ) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.get_file.return_value = None  # File doesn't exist
        mock_client.create_file.return_value = {"content": {"sha": "new123"}}
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/v1/vault/file",
            json={
                "path": "Inbox/new-note.md",
                "content": "# New Note\n\nContent here.",
            },
        )

        assert response.status_code == 200
        assert response.json()["status"] == "created"


def test_create_file_already_exists(client: TestClient) -> None:
    """Test creating a file that already exists."""
    with patch(
        "src.api.routes.vault.get_github_vault_client"
    ) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.get_file.return_value = {"content": "existing", "sha": "abc"}
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/v1/vault/file",
            json={
                "path": "existing.md",
                "content": "# New content",
            },
        )

        assert response.status_code == 409


def test_list_directory(client: TestClient) -> None:
    """Test listing vault directory."""
    mock_items = [
        {"name": "note1.md", "path": "Inbox/note1.md", "type": "file"},
        {"name": "subfolder", "path": "Inbox/subfolder", "type": "dir"},
    ]

    with patch(
        "src.api.routes.vault.get_github_vault_client"
    ) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.list_directory.return_value = mock_items
        mock_get_client.return_value = mock_client

        response = client.get("/api/v1/vault/directory", params={"path": "Inbox"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "note1.md"


def test_search_vault(client: TestClient) -> None:
    """Test searching the vault."""
    mock_results = [
        {"name": "meeting-notes.md", "path": "Project/meeting-notes.md"},
        {"name": "meetings.md", "path": "Area/meetings.md"},
    ]

    with patch(
        "src.api.routes.vault.get_github_vault_client"
    ) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.search_files.return_value = mock_results
        mock_get_client.return_value = mock_client

        response = client.get("/api/v1/vault/search", params={"query": "meeting"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


def test_get_daily_note(client: TestClient) -> None:
    """Test getting today's daily note."""
    mock_note = {
        "content": "# Daily Note\n\n## Tasks\n- [ ] Task 1",
        "sha": "daily123",
        "path": "Timestamps/2024/11/2024-11-22 Friday.md",
    }

    with patch(
        "src.api.routes.vault.get_github_vault_client"
    ) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.get_daily_note_path.return_value = mock_note["path"]
        mock_client.get_file.return_value = mock_note
        mock_get_client.return_value = mock_client

        response = client.get("/api/v1/vault/daily-note")

        assert response.status_code == 200
        data = response.json()
        assert "Daily Note" in data["content"]
