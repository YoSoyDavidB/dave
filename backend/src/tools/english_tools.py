"""English learning tools for the AI agent."""

from typing import Any

from src.core.english_service import get_error_stats, get_recent_corrections, log_correction

# Tool definitions for English learning
ENGLISH_TOOLS: list[dict[str, Any]] = [
    {
        "name": "log_english_correction",
        "description": (
            "Log an English correction to help the user track their learning "
            "progress. Use this when you correct a significant English mistake."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "original_text": {
                    "type": "string",
                    "description": "The original text with the error",
                },
                "corrected_text": {"type": "string", "description": "The corrected version"},
                "explanation": {
                    "type": "string",
                    "description": "Brief explanation of why it was wrong and the rule",
                },
                "category": {
                    "type": "string",
                    "enum": ["grammar", "vocabulary", "spelling", "expression"],
                    "description": "Category of the error",
                },
                "subcategory": {
                    "type": "string",
                    "description": (
                        "More specific type " "(e.g., 'verb_tense', 'articles', 'prepositions')"
                    ),
                },
            },
            "required": ["original_text", "corrected_text", "explanation", "category"],
        },
    },
    {
        "name": "get_english_progress",
        "description": (
            "Get the user's English learning progress and error statistics. "
            "Use when they ask about their progress or common mistakes."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_recent_english_errors",
        "description": (
            "Get recent English corrections to review. "
            "Use when the user wants to review their mistakes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days to look back (default: 7)",
                }
            },
            "required": [],
        },
    },
]


async def execute_english_tool(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Execute an English learning tool and return the result."""

    if tool_name == "log_english_correction":
        correction = await log_correction(
            original_text=tool_input["original_text"],
            corrected_text=tool_input["corrected_text"],
            explanation=tool_input["explanation"],
            category=tool_input["category"],
            subcategory=tool_input.get("subcategory"),
        )
        if correction:
            return f"Correction logged (#{correction.id}): {tool_input['category']}"
        return "Failed to log correction (database unavailable)"

    elif tool_name == "get_english_progress":
        stats = await get_error_stats()
        if stats["total_corrections"] == 0:
            return "No corrections logged yet. Keep practicing!"

        result = "📊 English Learning Progress:\n"
        result += f"Total corrections: {stats['total_corrections']}\n"
        result += f"Last 7 days: {stats['last_7_days']}\n\n"

        if stats["by_category"]:
            result += "By category:\n"
            for cat, count in stats["by_category"].items():
                result += f"  - {cat}: {count}\n"

        return result

    elif tool_name == "get_recent_english_errors":
        days = tool_input.get("days", 7)
        corrections = await get_recent_corrections(days=days)

        if not corrections:
            return f"No corrections in the last {days} days. Great job!"

        result = f"📝 Recent corrections (last {days} days):\n\n"
        for c in corrections[:10]:
            result += f"❌ {c.original_text}\n"
            result += f"✅ {c.corrected_text}\n"
            result += f"📖 {c.explanation}\n"
            result += f"[{c.category}] {c.created_at.strftime('%Y-%m-%d')}\n\n"

        return result

    return f"Unknown English tool: {tool_name}"
