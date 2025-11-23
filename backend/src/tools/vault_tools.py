"""Vault tools for the AI agent."""

import re
from datetime import datetime, timedelta
from typing import Any

from src.infrastructure.github_vault import get_github_vault_client

# Path to the daily note template in the vault
DAILY_NOTE_TEMPLATE_PATH = "Extras/Templates/Template, Daily log.md"


def _process_templater_syntax(template: str, date: datetime) -> str:
    """Process Templater syntax in a template string."""
    month_names = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    yesterday = date - timedelta(days=1)
    tomorrow = date + timedelta(days=1)

    # Build replacement map for common Templater patterns
    result = template

    # Replace tp.file.creation_date()
    result = re.sub(
        r'<%\s*tp\.file\.creation_date\(\)\s*%>',
        date.strftime("%Y-%m-%d"),
        result
    )

    # Replace moment formatting for title
    result = re.sub(
        r'<%\s*moment\(tp\.file\.title,[\'"]YYYY-MM-DD[\'"]\)\.format\([\'"]dddd, MMMM DD, YYYY[\'"]\)\s*%>',
        f"{day_names[date.weekday()]}, {month_names[date.month]} {date.day:02d}, {date.year}",
        result
    )

    # Replace tp.date.now patterns for yesterday (offset -1)
    def replace_yesterday(match: re.Match) -> str:
        fmt = match.group(1)
        if fmt == "YYYY":
            return str(yesterday.year)
        elif fmt == "MM-MMMM":
            return f"{yesterday.month:02d}-{month_names[yesterday.month]}"
        elif fmt == "YYYY-MM-DD-dddd":
            return f"{yesterday.strftime('%Y-%m-%d')}-{day_names[yesterday.weekday()]}"
        return match.group(0)

    result = re.sub(
        r'<%\s*tp\.date\.now\([\'"]([^"\']+)[\'"],\s*-1\)\s*%>',
        replace_yesterday,
        result
    )

    # Replace tp.date.now patterns for tomorrow (offset 1)
    def replace_tomorrow(match: re.Match) -> str:
        fmt = match.group(1)
        if fmt == "YYYY":
            return str(tomorrow.year)
        elif fmt == "MM-MMMM":
            return f"{tomorrow.month:02d}-{month_names[tomorrow.month]}"
        elif fmt == "YYYY-MM-DD-dddd":
            return f"{tomorrow.strftime('%Y-%m-%d')}-{day_names[tomorrow.weekday()]}"
        return match.group(0)

    result = re.sub(
        r'<%\s*tp\.date\.now\([\'"]([^"\']+)[\'"],\s*1\)\s*%>',
        replace_tomorrow,
        result
    )

    # Replace tp.date.now for current date (no offset)
    result = re.sub(
        r'<%\s*tp\.date\.now\([\'"]YYYY-MM-DD[\'"]\)\s*%>',
        date.strftime("%Y-%m-%d"),
        result
    )

    return result


async def _get_daily_note_template(client: Any) -> str | None:
    """Fetch and process the daily note template from the vault."""
    template_file = await client.get_file(DAILY_NOTE_TEMPLATE_PATH)
    if template_file is None:
        return None
    return str(template_file["content"])

# Tool definitions for OpenRouter/Claude
VAULT_TOOLS: list[dict[str, Any]] = [
    {
        "name": "read_note",
        "description": (
            "Read a note from the user's Obsidian vault. "
            "Use this to access existing notes, daily notes, or any markdown file."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": (
                        "Path to the note relative to vault root. "
                        "Examples: 'Inbox/quick-note.md', 'Area/Terapia/autoregistro.md'"
                    )
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "read_daily_note",
        "description": (
            "Read today's daily note from the vault. "
            "Use this when the user asks about their day, tasks, or daily activities."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "create_note",
        "description": (
            "Create a new note in the user's Obsidian vault. "
            "Use this to help organize thoughts, create tasks, or save information."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": (
                        "Path for the new note. "
                        "Examples: 'Inbox/meeting-notes.md', 'Project/Personal/idea.md'"
                    )
                },
                "content": {
                    "type": "string",
                    "description": "Markdown content for the note. Include frontmatter if needed."
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "list_directory",
        "description": (
            "List files and folders in a vault directory. "
            "Use to explore the vault structure or find specific notes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": (
                        "Directory path. Use '' for root. "
                        "Examples: 'Inbox', 'Project/Personal'"
                    )
                }
            },
            "required": []
        }
    },
    {
        "name": "search_vault",
        "description": (
            "Search for notes in the vault by content or filename. "
            "Use when looking for specific information."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to find relevant notes"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "append_to_daily_note",
        "description": (
            "Add content to today's daily note. "
            "Use for quick capture, adding tasks, or logging activities. "
            "If the daily note doesn't exist, use create_daily_note first."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "description": (
                        "Section to append to: "
                        "'quick_capture', 'notes', 'tasks', 'gastos', 'english'"
                    )
                },
                "content": {
                    "type": "string",
                    "description": "Content to add to the section"
                }
            },
            "required": ["section", "content"]
        }
    },
    {
        "name": "create_daily_note",
        "description": (
            "Create today's daily note with the standard template. "
            "Use this when the user wants to add something to their daily note "
            "but it doesn't exist yet."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


async def execute_tool(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Execute a vault tool and return the result."""
    client = get_github_vault_client()

    if tool_name == "read_note":
        result = await client.get_file(tool_input["path"])
        if result is None:
            return f"Note not found: {tool_input['path']}"
        return str(result["content"])

    elif tool_name == "read_daily_note":
        path = await client.get_daily_note_path()
        result = await client.get_file(path)
        if result is None:
            return f"Daily note not found for today. Path would be: {path}"
        return str(result["content"])

    elif tool_name == "create_note":
        existing = await client.get_file(tool_input["path"])
        if existing is not None:
            return f"Note already exists: {tool_input['path']}"
        await client.create_file(
            path=tool_input["path"],
            content=tool_input["content"],
        )
        return f"Note created: {tool_input['path']}"

    elif tool_name == "list_directory":
        path = tool_input.get("path", "")
        items = await client.list_directory(path)
        if not items:
            return f"Empty or not found: {path}"
        lines: list[str] = []
        for item in items:
            icon = "📁" if item["type"] == "dir" else "📄"
            lines.append(f"{icon} {item['name']}")
        return "\n".join(lines)

    elif tool_name == "search_vault":
        results = await client.search_files(tool_input["query"])
        if not results:
            return f"No results found for: {tool_input['query']}"
        return "\n".join([f"📄 {r['path']}" for r in results])

    elif tool_name == "append_to_daily_note":
        path = await client.get_daily_note_path()
        note = await client.get_file(path)

        # Auto-create daily note if it doesn't exist
        if note is None:
            today = datetime.now()
            # Try to get template from vault
            template_content = await _get_daily_note_template(client)
            if template_content:
                # Process Templater syntax
                processed_content = _process_templater_syntax(template_content, today)
            else:
                # Fallback to basic template if vault template not found
                day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                month_names = ["", "January", "February", "March", "April", "May", "June",
                              "July", "August", "September", "October", "November", "December"]
                processed_content = f"""---
created: {today.strftime("%Y-%m-%d")}
tags:
  - DailyNotes
---

# {day_names[today.weekday()]}, {month_names[today.month]} {today.day:02d}, {today.year}

## 📥 Quick Capture
-

## 📝 Notes
-

## 💰 Gastos del día
-
"""
            await client.create_file(path=path, content=processed_content)
            # Re-fetch the note we just created
            note = await client.get_file(path)
            if note is None:
                return "Failed to create daily note"

        content = str(note["content"])
        section = tool_input.get("section", "quick_capture")
        new_content = tool_input.get("content", "")

        if not new_content:
            return "Error: No content provided to add"

        # Find section and append
        section_markers = {
            "quick_capture": "## 📥 Quick Capture",
            "notes": "## 📝 Notes",
            "tasks": "##### 🚀 Things I plan to accomplish today are...",
            "gastos": "## 💰 Gastos del día",
            "english": "## 🇬🇧 English Practice",
        }

        marker = section_markers.get(section)
        if marker and marker in content:
            # Find the marker and add after the next line
            idx = content.find(marker)
            next_line = content.find("\n", idx)
            if next_line != -1:
                # Find end of section (next ## or end)
                section_content_start = next_line + 1
                # Skip any description lines starting with >
                while section_content_start < len(content):
                    if content[section_content_start] == ">":
                        section_content_start = content.find("\n", section_content_start) + 1
                    elif content[section_content_start] == "\n":
                        section_content_start += 1
                    else:
                        break

                # Insert the new content
                updated = (
                    content[:section_content_start]
                    + f"- {new_content}\n"
                    + content[section_content_start:]
                )

                await client.update_file(
                    path=path,
                    content=updated,
                    sha=str(note["sha"]),
                )
                return f"Added to {section}: {new_content}"

        return f"Section '{section}' not found in daily note"

    elif tool_name == "create_daily_note":
        path = await client.get_daily_note_path()
        existing = await client.get_file(path)
        if existing is not None:
            return f"Daily note already exists: {path}"

        today = datetime.now()
        # Try to get template from vault
        template_content = await _get_daily_note_template(client)
        if template_content:
            # Process Templater syntax
            processed_content = _process_templater_syntax(template_content, today)
        else:
            # Fallback to basic template if vault template not found
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            month_names = ["", "January", "February", "March", "April", "May", "June",
                          "July", "August", "September", "October", "November", "December"]
            processed_content = f"""---
created: {today.strftime("%Y-%m-%d")}
tags:
  - DailyNotes
---

# {day_names[today.weekday()]}, {month_names[today.month]} {today.day:02d}, {today.year}

## 📥 Quick Capture
-

## 📝 Notes
-

## 💰 Gastos del día
-
"""

        await client.create_file(path=path, content=processed_content)
        return f"Daily note created: {path}"

    return f"Unknown tool: {tool_name}"
