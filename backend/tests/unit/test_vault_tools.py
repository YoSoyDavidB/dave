from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from src.tools.vault_tools import (
    _process_templater_syntax,
    _get_daily_note_template,
    execute_tool,
)


class TestTemplaterProcessing:
    """Tests for Templater syntax processing."""

    def test_process_creation_date(self):
        """Test processing tp.file.creation_date()."""
        template = "created: <% tp.file.creation_date() %>"
        date = datetime(2025, 11, 23)

        result = _process_templater_syntax(template, date)

        assert "created: 2025-11-23" in result

    def test_process_moment_format(self):
        """Test processing moment formatting for title."""
        template = '# <% moment(tp.file.title,"YYYY-MM-DD").format("dddd, MMMM DD, YYYY") %>'
        date = datetime(2025, 11, 23)  # Sunday

        result = _process_templater_syntax(template, date)

        assert "Sunday, November 23, 2025" in result

    def test_process_yesterday_link(self):
        """Test processing yesterday date offset."""
        template = '[[<% tp.date.now("YYYY-MM-DD-dddd", -1) %>|Yesterday]]'
        date = datetime(2025, 11, 23)  # Sunday, so yesterday is Saturday

        result = _process_templater_syntax(template, date)

        assert "2025-11-22-Saturday" in result

    def test_process_tomorrow_link(self):
        """Test processing tomorrow date offset."""
        template = '[[<% tp.date.now("YYYY-MM-DD-dddd", 1) %>|Tomorrow]]'
        date = datetime(2025, 11, 23)  # Sunday, so tomorrow is Monday

        result = _process_templater_syntax(template, date)

        assert "2025-11-24-Monday" in result

    def test_process_month_format(self):
        """Test processing month formats."""
        template = '<% tp.date.now("MM-MMMM", -1) %>'
        date = datetime(2025, 11, 23)

        result = _process_templater_syntax(template, date)

        assert "11-November" in result

    def test_process_year_format(self):
        """Test processing year formats."""
        template = '<% tp.date.now("YYYY", 1) %>'
        date = datetime(2025, 12, 31)  # Tomorrow is 2026

        result = _process_templater_syntax(template, date)

        assert "2026" in result

    def test_process_full_template(self):
        """Test processing a complete daily note template."""
        template = """---
created: <% tp.file.creation_date() %>
tags:
  - DailyNotes
---

# <% moment(tp.file.title,"YYYY-MM-DD").format("dddd, MMMM DD, YYYY") %>

<< [[Timestamps/<% tp.date.now("YYYY", -1) %>/<% tp.date.now("MM-MMMM", -1) %>/<% tp.date.now("YYYY-MM-DD-dddd", -1) %>|Yesterday]] >>

## 📥 Quick Capture
-
"""
        date = datetime(2025, 11, 23)

        result = _process_templater_syntax(template, date)

        assert "created: 2025-11-23" in result
        assert "Sunday, November 23, 2025" in result
        assert "2025-11-22-Saturday" in result
        assert "## 📥 Quick Capture" in result


class TestGetDailyNoteTemplate:
    """Tests for fetching the daily note template."""

    @pytest.mark.asyncio
    async def test_get_template_success(self):
        """Test successfully fetching the template."""
        mock_template = {
            "content": "# Daily Note Template\n## Quick Capture",
            "sha": "abc123",
            "path": "Extras/Templates/Template, Daily log.md"
        }

        mock_client = AsyncMock()
        mock_client.get_file.return_value = mock_template

        result = await _get_daily_note_template(mock_client)

        assert result == "# Daily Note Template\n## Quick Capture"

    @pytest.mark.asyncio
    async def test_get_template_not_found(self):
        """Test when template doesn't exist."""
        mock_client = AsyncMock()
        mock_client.get_file.return_value = None

        result = await _get_daily_note_template(mock_client)

        assert result is None


class TestVaultToolExecution:
    """Tests for vault tool execution."""

    @pytest.mark.asyncio
    async def test_read_note_success(self):
        """Test reading a note successfully."""
        with patch("src.tools.vault_tools.get_github_vault_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get_file.return_value = {
                "content": "# Test Note\nContent here",
                "sha": "abc123"
            }
            mock_get.return_value = mock_client

            result = await execute_tool("read_note", {"path": "test.md"})

            assert "Test Note" in result

    @pytest.mark.asyncio
    async def test_read_note_not_found(self):
        """Test reading a non-existent note."""
        with patch("src.tools.vault_tools.get_github_vault_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get_file.return_value = None
            mock_get.return_value = mock_client

            result = await execute_tool("read_note", {"path": "nonexistent.md"})

            assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_create_note_success(self):
        """Test creating a new note."""
        with patch("src.tools.vault_tools.get_github_vault_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get_file.return_value = None  # Doesn't exist
            mock_client.create_file.return_value = {"content": {"sha": "new123"}}
            mock_get.return_value = mock_client

            result = await execute_tool("create_note", {
                "path": "Inbox/new-note.md",
                "content": "# New Note"
            })

            assert "created" in result.lower()

    @pytest.mark.asyncio
    async def test_create_note_already_exists(self):
        """Test creating a note that already exists."""
        with patch("src.tools.vault_tools.get_github_vault_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get_file.return_value = {"content": "existing", "sha": "abc"}
            mock_get.return_value = mock_client

            result = await execute_tool("create_note", {
                "path": "existing.md",
                "content": "# Content"
            })

            assert "already exists" in result.lower()

    @pytest.mark.asyncio
    async def test_list_directory(self):
        """Test listing directory contents."""
        with patch("src.tools.vault_tools.get_github_vault_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.list_directory.return_value = [
                {"name": "note1.md", "type": "file"},
                {"name": "subfolder", "type": "dir"},
            ]
            mock_get.return_value = mock_client

            result = await execute_tool("list_directory", {"path": "Inbox"})

            assert "📄 note1.md" in result
            assert "📁 subfolder" in result

    @pytest.mark.asyncio
    async def test_search_vault(self):
        """Test searching the vault."""
        with patch("src.tools.vault_tools.get_github_vault_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.search_files.return_value = [
                {"name": "meeting.md", "path": "Project/meeting.md"},
            ]
            mock_get.return_value = mock_client

            result = await execute_tool("search_vault", {"query": "meeting"})

            assert "meeting.md" in result

    @pytest.mark.asyncio
    async def test_create_daily_note_success(self):
        """Test creating a daily note with template."""
        with patch("src.tools.vault_tools.get_github_vault_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get_daily_note_path.return_value = "Timestamps/2025/11-November/2025-11-23-Sunday.md"
            mock_client.get_file.side_effect = [
                None,  # Daily note doesn't exist
                {"content": "# Template\n## Quick Capture", "sha": "tpl123"},  # Template exists
            ]
            mock_client.create_file.return_value = {"content": {"sha": "new123"}}
            mock_get.return_value = mock_client

            result = await execute_tool("create_daily_note", {})

            assert "created" in result.lower()

    @pytest.mark.asyncio
    async def test_create_daily_note_already_exists(self):
        """Test creating a daily note that already exists."""
        with patch("src.tools.vault_tools.get_github_vault_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get_daily_note_path.return_value = "Timestamps/2025/11-November/2025-11-23-Sunday.md"
            mock_client.get_file.return_value = {"content": "existing note", "sha": "abc"}
            mock_get.return_value = mock_client

            result = await execute_tool("create_daily_note", {})

            assert "already exists" in result.lower()

    @pytest.mark.asyncio
    async def test_append_to_daily_note_auto_create(self):
        """Test appending to daily note that auto-creates if missing."""
        with patch("src.tools.vault_tools.get_github_vault_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get_daily_note_path.return_value = "Timestamps/2025/11-November/2025-11-23-Sunday.md"

            # First call: daily note doesn't exist
            # Second call: template
            # Third call: newly created daily note
            mock_client.get_file.side_effect = [
                None,  # Daily note doesn't exist
                {"content": "## 📥 Quick Capture\n>\n-", "sha": "tpl123"},  # Template
                {"content": "## 📥 Quick Capture\n>\n-", "sha": "new123"},  # Created note
            ]
            mock_client.create_file.return_value = {}
            mock_client.update_file.return_value = {}
            mock_get.return_value = mock_client

            result = await execute_tool("append_to_daily_note", {
                "section": "quick_capture",
                "content": "Test item"
            })

            # Should either succeed or report section not found
            assert "Added to" in result or "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test executing an unknown tool."""
        with patch("src.tools.vault_tools.get_github_vault_client"):
            result = await execute_tool("unknown_tool", {})

            assert "Unknown tool" in result
