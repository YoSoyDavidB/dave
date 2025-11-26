import base64
from datetime import datetime
from typing import Any
from urllib.parse import quote

import httpx
import structlog

from src.config import get_settings

logger = structlog.get_logger()


class GitHubVaultClient:
    """Client for accessing Obsidian vault via GitHub API."""

    def __init__(self) -> None:
        settings = get_settings()
        self.token = settings.github_token
        self.repo = settings.github_repo  # format: "username/repo"
        self.vault_prefix = settings.vault_path_prefix
        self.base_url = "https://api.github.com"

    def _full_path(self, path: str) -> str:
        """Get full path including vault prefix."""
        if self.vault_prefix:
            return f"{self.vault_prefix}/{path}" if path else self.vault_prefix
        return path

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_file(self, path: str) -> dict[str, Any] | None:
        """Get a file from the vault.

        Returns dict with 'content' and 'sha' or None if not found.
        """
        full_path = self._full_path(path)
        # Quote the path to handle special characters, but keep slashes
        encoded_path = quote(full_path, safe="/")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{self.repo}/contents/{encoded_path}",
                headers=self.headers,
                timeout=30.0,
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            data = response.json()

            # Decode base64 content
            content = base64.b64decode(data["content"]).decode("utf-8")

            # Return path relative to vault prefix, not the full GitHub path
            relative_path = data["path"]
            if self.vault_prefix and relative_path.startswith(self.vault_prefix + "/"):
                relative_path = relative_path[len(self.vault_prefix) + 1 :]

            logger.info("vault_file_read", path=path)
            return {
                "content": content,
                "sha": data["sha"],
                "path": relative_path,
            }

    async def create_file(
        self,
        path: str,
        content: str,
        message: str | None = None,
    ) -> dict[str, Any]:
        """Create a new file in the vault."""
        full_path = self._full_path(path)
        if message is None:
            message = f"Create {path} via Dave"

        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        encoded_path = quote(full_path, safe="/")

        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/repos/{self.repo}/contents/{encoded_path}",
                headers=self.headers,
                json={
                    "message": message,
                    "content": encoded_content,
                },
                timeout=30.0,
            )
            response.raise_for_status()

            logger.info("vault_file_created", path=path)
            result: dict[str, Any] = response.json()
            return result

    async def update_file(
        self,
        path: str,
        content: str,
        sha: str,
        message: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing file in the vault."""
        full_path = self._full_path(path)
        if message is None:
            message = f"Update {path} via Dave"

        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        encoded_path = quote(full_path, safe="/")

        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/repos/{self.repo}/contents/{encoded_path}",
                headers=self.headers,
                json={
                    "message": message,
                    "content": encoded_content,
                    "sha": sha,
                },
                timeout=30.0,
            )
            response.raise_for_status()

            logger.info("vault_file_updated", path=path)
            result: dict[str, Any] = response.json()
            return result

    async def list_directory(self, path: str = "") -> list[dict[str, str]]:
        """List files in a directory."""
        full_path = self._full_path(path)
        encoded_path = quote(full_path, safe="/") if full_path else ""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{self.repo}/contents/{encoded_path}",
                headers=self.headers,
                timeout=30.0,
            )

            if response.status_code == 404:
                return []

            response.raise_for_status()
            data = response.json()

            # Filter to only markdown files and directories
            items: list[dict[str, str]] = []
            for item in data:
                if item["type"] == "dir" or item["name"].endswith(".md"):
                    # Return path relative to vault prefix, not the full GitHub path
                    relative_path = item["path"]
                    if self.vault_prefix and relative_path.startswith(self.vault_prefix + "/"):
                        relative_path = relative_path[len(self.vault_prefix) + 1 :]
                    items.append(
                        {
                            "name": item["name"],
                            "path": relative_path,
                            "type": item["type"],
                        }
                    )

            logger.info("vault_directory_listed", path=path, count=len(items))
            return items

    async def search_files(self, query: str) -> list[dict[str, str]]:
        """Search for files in the vault."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search/code",
                headers=self.headers,
                params={
                    "q": f"{query} repo:{self.repo} extension:md",
                    "per_page": 20,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            results: list[dict[str, str]] = []
            for item in data.get("items", []):
                # Return path relative to vault prefix
                relative_path = item["path"]
                if self.vault_prefix and relative_path.startswith(self.vault_prefix + "/"):
                    relative_path = relative_path[len(self.vault_prefix) + 1 :]
                results.append(
                    {
                        "name": item["name"],
                        "path": relative_path,
                    }
                )

            logger.info("vault_search", query=query, results=len(results))
            return results

    async def get_daily_note_path(self, date: datetime | None = None) -> str:
        """Get the path for a daily note."""
        if date is None:
            date = datetime.now()

        # Format: Timestamps/YYYY/MM-Month/YYYY-MM-DD Day.md
        month_names = [
            "",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        year = date.strftime("%Y")
        month_num = date.strftime("%m")
        month_name = month_names[date.month]
        day = date.strftime("%Y-%m-%d")
        day_name = day_names[date.weekday()]

        return f"Timestamps/{year}/{month_num}-{month_name}/{day}-{day_name}.md"


def get_github_vault_client() -> GitHubVaultClient:
    """Get GitHub vault client instance."""
    return GitHubVaultClient()
