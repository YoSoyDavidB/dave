---
created: 2024-11-22
tags:
  - project
  - AI
  - architecture
status: draft
---

# 🏗️ Dave - Technical Architecture

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Dave SYSTEM                                │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────────────────────┐
│ React + Vite │────▶│   FastAPI    │────▶│        Agent Core            │
│   Frontend   │◀────│   Backend    │◀────│   (LLM + Tools + Memory)     │
└──────────────┘     └──────────────┘     └──────────────────────────────┘
       │                    │                          │
       │              ┌─────┴─────┐                    │
       │              │           │                    │
       ▼              ▼           ▼                    ▼
┌──────────────┐ ┌─────────┐ ┌─────────┐     ┌──────────────────┐
│  WebSocket   │ │  Redis  │ │ Celery  │     │  External APIs   │
│  (Streaming) │ │ (Cache) │ │ (Queue) │     │  (LLM, GitHub)   │
└──────────────┘ └─────────┘ └─────────┘     └──────────────────┘
```

---

## 2. Directory Structure

```
dave/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry
│   │   ├── config.py                  # Settings & env vars
│   │   │
│   │   ├── api/                       # API Layer
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── chat.py            # Chat endpoints
│   │   │   │   ├── obsidian.py        # Obsidian endpoints
│   │   │   │   ├── english.py         # English progress endpoints
│   │   │   │   └── health.py          # Health checks
│   │   │   ├── middleware/
│   │   │   │   ├── auth.py
│   │   │   │   └── logging.py
│   │   │   └── schemas/               # Pydantic models
│   │   │       ├── chat.py
│   │   │       ├── obsidian.py
│   │   │       └── english.py
│   │   │
│   │   ├── core/                      # Business Logic
│   │   │   ├── __init__.py
│   │   │   ├── agent/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dave_agent.py     # Main agent orchestrator
│   │   │   │   ├── personality.py     # System prompts & persona
│   │   │   │   └── context.py         # Context management
│   │   │   ├── english/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── analyzer.py        # Analyze user messages
│   │   │   │   ├── corrector.py       # Generate corrections
│   │   │   │   └── tracker.py         # Track progress
│   │   │   └── productivity/
│   │   │       ├── __init__.py
│   │   │       ├── task_extractor.py  # Extract tasks from chat
│   │   │       └── reminder.py        # Proactive reminders
│   │   │
│   │   ├── tools/                     # Agent Tools
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Base tool class
│   │   │   ├── obsidian/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── create_note.py
│   │   │   │   ├── search_notes.py
│   │   │   │   ├── create_daily.py
│   │   │   │   └── create_person.py
│   │   │   ├── calendar/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── google_calendar.py
│   │   │   │   └── outlook_calendar.py
│   │   │   └── email/
│   │   │       ├── __init__.py
│   │   │       ├── gmail.py
│   │   │       └── outlook.py
│   │   │
│   │   ├── infrastructure/            # External Services
│   │   │   ├── __init__.py
│   │   │   ├── llm/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── openrouter.py      # OpenRouter client
│   │   │   │   └── models.py          # Model configs
│   │   │   ├── vector_store/
│   │   │   │   ├── __init__.py
│   │   │   │   └── qdrant.py          # Qdrant client
│   │   │   ├── graph/
│   │   │   │   ├── __init__.py
│   │   │   │   └── neo4j.py           # Neo4j client
│   │   │   ├── github/
│   │   │   │   ├── __init__.py
│   │   │   │   └── client.py          # GitHub API for Obsidian
│   │   │   └── cache/
│   │   │       ├── __init__.py
│   │   │       └── redis.py           # Redis client
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logging.py             # Structured logging
│   │       └── helpers.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py                # Pytest fixtures
│   │   ├── unit/
│   │   │   ├── test_english_analyzer.py
│   │   │   ├── test_task_extractor.py
│   │   │   └── test_obsidian_tools.py
│   │   ├── integration/
│   │   │   ├── test_agent_flow.py
│   │   │   ├── test_github_integration.py
│   │   │   └── test_qdrant.py
│   │   └── e2e/
│   │       └── test_chat_flow.py
│   │
│   ├── alembic/                       # DB migrations (if needed)
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── poetry.lock
│   └── pytest.ini
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx                   # App entry point
│   │   ├── App.tsx                    # Root component
│   │   ├── index.css                  # Global styles (Tailwind)
│   │   │
│   │   ├── pages/                     # Page components
│   │   │   ├── Chat.tsx               # Main chat page
│   │   │   └── Dashboard.tsx          # Stats dashboard
│   │   │
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatWindow.tsx
│   │   │   │   ├── Message.tsx
│   │   │   │   ├── MessageInput.tsx
│   │   │   │   ├── EnglishCorrection.tsx
│   │   │   │   └── ToolIndicator.tsx
│   │   │   ├── ui/                    # Reusable UI components
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   └── Input.tsx
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   └── Layout.tsx
│   │   │   └── dashboard/
│   │   │       ├── StatsCard.tsx
│   │   │       └── ProgressChart.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useChat.ts
│   │   │   ├── useWebSocket.ts
│   │   │   └── useEnglishStats.ts
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts                 # API client (fetch wrapper)
│   │   │   └── utils.ts
│   │   │
│   │   ├── stores/
│   │   │   └── chatStore.ts           # Zustand store
│   │   │
│   │   └── types/
│   │       └── index.ts
│   │
│   ├── public/
│   ├── index.html                     # HTML entry point
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── vite.config.ts                 # Vite configuration
│
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── Makefile
└── README.md
```

---

## 3. Core Components

### 3.1 Agent Core (dave_agent.py)

```python
# backend/src/core/agent/dave_agent.py

from typing import AsyncGenerator
from src.infrastructure.llm import OpenRouterClient
from src.core.english import EnglishAnalyzer, EnglishCorrector
from src.tools import ToolRegistry

class DaveAgent:
    """
    Main agent that orchestrates:
    - LLM calls
    - Tool execution
    - English correction
    - Memory management
    """

    def __init__(
        self,
        llm_client: OpenRouterClient,
        english_analyzer: EnglishAnalyzer,
        english_corrector: EnglishCorrector,
        tool_registry: ToolRegistry,
        memory_service: MemoryService,
    ):
        self.llm = llm_client
        self.english_analyzer = english_analyzer
        self.english_corrector = english_corrector
        self.tools = tool_registry
        self.memory = memory_service

    async def chat(
        self,
        message: str,
        conversation_id: str | None = None
    ) -> AsyncGenerator[ChatChunk, None]:
        """
        Process a user message and stream the response.

        Flow:
        1. Analyze English in user message
        2. Retrieve relevant context from memory
        3. Call LLM with tools
        4. Execute any tool calls
        5. Generate corrections
        6. Stream response
        7. Save to memory
        """
        # 1. Analyze user's English
        english_analysis = await self.english_analyzer.analyze(message)

        # 2. Get context
        context = await self.memory.get_relevant_context(
            message,
            conversation_id
        )

        # 3. Build messages
        messages = self._build_messages(message, context)

        # 4. Call LLM with streaming
        async for chunk in self.llm.chat_stream(
            messages=messages,
            tools=self.tools.get_tool_definitions(),
        ):
            if chunk.type == "tool_call":
                # Execute tool
                result = await self.tools.execute(
                    chunk.tool_name,
                    chunk.tool_args
                )
                yield ChatChunk(type="tool_result", data=result)
            else:
                yield chunk

        # 5. Generate corrections (after main response)
        if english_analysis.has_errors:
            corrections = await self.english_corrector.generate(
                english_analysis
            )
            yield ChatChunk(type="corrections", data=corrections)

        # 6. Save to memory
        await self.memory.save_interaction(
            conversation_id=conversation_id,
            user_message=message,
            assistant_response=full_response,
            corrections=corrections,
        )
```

### 3.2 English Analyzer

```python
# backend/src/core/english/analyzer.py

from pydantic import BaseModel
from src.infrastructure.llm import OpenRouterClient

class EnglishError(BaseModel):
    original: str
    category: str  # "grammar" | "naturalness" | "vocabulary"
    severity: str  # "minor" | "major"

class EnglishAnalysis(BaseModel):
    original_text: str
    errors: list[EnglishError]
    has_errors: bool

class EnglishAnalyzer:
    """Analyzes user messages for English errors."""

    ANALYSIS_PROMPT = """
    Analyze the following text written by a Spanish native speaker
    learning English. Identify:

    1. Grammar errors (verb tense, articles, prepositions, etc.)
    2. Unnatural phrasing (correct but sounds non-native)
    3. Vocabulary issues (wrong word choice, false friends)

    Text: {text}

    Return JSON with errors found. Be constructive, not critical.
    """

    async def analyze(self, text: str) -> EnglishAnalysis:
        # Use a fast, cheap model for analysis
        response = await self.llm.complete(
            self.ANALYSIS_PROMPT.format(text=text),
            model="gpt-3.5-turbo",  # Fast and cheap
            response_format="json"
        )
        return EnglishAnalysis.model_validate(response)
```

### 3.3 Tool Definition Example

```python
# backend/src/tools/obsidian/create_daily.py

from src.tools.base import BaseTool
from src.infrastructure.github import GitHubClient

class CreateDailyNoteTool(BaseTool):
    """Creates a daily note in Obsidian vault."""

    name = "create_daily_note"
    description = """
    Creates a daily note for today (or specified date) in the Obsidian vault.
    Use this when the user wants to log their day, create a journal entry,
    or start their daily planning.
    """

    parameters = {
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "Date for the note (YYYY-MM-DD). Defaults to today.",
            },
            "content": {
                "type": "object",
                "description": "Content to add to the daily note",
                "properties": {
                    "accomplishments": {"type": "array", "items": {"type": "string"}},
                    "tasks": {"type": "array", "items": {"type": "string"}},
                    "notes": {"type": "string"},
                    "mood": {"type": "string"},
                }
            }
        },
        "required": []
    }

    async def execute(self, date: str | None = None, content: dict | None = None) -> str:
        date = date or datetime.now().strftime("%Y-%m-%d")

        # Build note from template
        note_content = self._build_daily_note(date, content)

        # Calculate path: Timestamps/2024/11-November/2024-11-22-Friday.md
        path = self._get_daily_note_path(date)

        # Create/update via GitHub API
        await self.github.create_or_update_file(
            path=path,
            content=note_content,
            message=f"Daily note for {date} via Dave"
        )

        return f"Created daily note for {date}"
```

---

## 4. Data Flow

### 4.1 Chat Flow

```
User Message
     │
     ▼
┌─────────────────┐
│  API Gateway    │ ─── Auth check
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ English Analyzer│ ─── Detect errors (async, non-blocking)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Memory Service  │ ─── Fetch relevant context
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   LLM Call      │ ─── With tools & context
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│ Text  │ │ Tool  │
│ Chunk │ │ Call  │
└───┬───┘ └───┬───┘
    │         │
    │    ┌────┴────┐
    │    │ Execute │
    │    │  Tool   │
    │    └────┬────┘
    │         │
    ▼         ▼
┌─────────────────┐
│ Stream Response │ ─── WebSocket to frontend
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Add Corrections │ ─── If errors detected
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Save to Memory  │ ─── Qdrant + Neo4j
└─────────────────┘
```

### 4.2 Obsidian Sync Flow

```
Dave creates/modifies note
          │
          ▼
┌─────────────────┐
│  GitHub API     │ ─── Commit to repo
└────────┬────────┘
          │
          ▼
┌─────────────────┐
│  GitHub Repo    │ ─── David's vault repo
└────────┬────────┘
          │
     (5 min sync)
          │
          ▼
┌─────────────────┐
│  Obsidian       │ ─── Auto-pulls changes
│  (Local)        │
└─────────────────┘
```

---

## 5. API Specifications

### 5.1 Chat Endpoint

```yaml
POST /api/v1/chat
Content-Type: application/json

Request:
{
  "message": "I need to schedule a meeting with John tomorrow",
  "conversation_id": "uuid-optional"
}

Response (Server-Sent Events):
event: chunk
data: {"type": "text", "content": "Sure! "}

event: chunk
data: {"type": "text", "content": "Let me check your calendar..."}

event: chunk
data: {"type": "tool_start", "tool": "search_calendar", "args": {...}}

event: chunk
data: {"type": "tool_result", "result": "You have 3 meetings tomorrow..."}

event: chunk
data: {"type": "text", "content": "You're pretty busy tomorrow! ..."}

event: corrections
data: {
  "corrections": [
    {
      "original": "I need to schedule a meeting",
      "suggestion": "I need to set up a meeting",
      "explanation": "'Set up' sounds more natural for arranging meetings",
      "category": "naturalness"
    }
  ]
}

event: done
data: {"conversation_id": "uuid", "message_id": "uuid"}
```

### 5.2 WebSocket for Real-time

```typescript
// Frontend WebSocket connection
const ws = new WebSocket('wss://api.dave.app/ws/chat');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch(data.type) {
    case 'text':
      appendToMessage(data.content);
      break;
    case 'tool_start':
      showToolIndicator(data.tool);
      break;
    case 'corrections':
      showCorrections(data.corrections);
      break;
  }
};
```

---

## 6. Testing Strategy

### 6.1 Test Pyramid

```
          /\
         /  \      E2E Tests (10%)
        /────\     - Full chat flows
       /      \    - Integration with real APIs (staging)
      /────────\
     /          \  Integration Tests (30%)
    /            \ - Agent + Tools
   /──────────────\- LLM mocking
  /                \- Database interactions
 /──────────────────\
/                    \ Unit Tests (60%)
/______________________\- English analyzer
                        - Task extractor
                        - Tool logic
                        - Helpers
```

### 6.2 Example Tests

```python
# tests/unit/test_english_analyzer.py

import pytest
from src.core.english.analyzer import EnglishAnalyzer

class TestEnglishAnalyzer:

    @pytest.fixture
    def analyzer(self, mock_llm):
        return EnglishAnalyzer(llm=mock_llm)

    async def test_detects_grammar_error(self, analyzer):
        """Should detect missing article."""
        text = "I went to office yesterday"

        result = await analyzer.analyze(text)

        assert result.has_errors
        assert any(e.category == "grammar" for e in result.errors)
        assert "article" in result.errors[0].explanation.lower()

    async def test_detects_unnatural_phrasing(self, analyzer):
        """Should suggest more natural alternatives."""
        text = "I have 25 years"  # Spanish interference

        result = await analyzer.analyze(text)

        assert result.has_errors
        assert any(e.category == "naturalness" for e in result.errors)

    async def test_no_errors_for_correct_text(self, analyzer):
        """Should not flag correct English."""
        text = "I went to the office yesterday"

        result = await analyzer.analyze(text)

        assert not result.has_errors


# tests/integration/test_agent_flow.py

class TestAgentFlow:

    async def test_creates_daily_note_from_chat(
        self,
        agent: DaveAgent,
        mock_github: MockGitHub
    ):
        """Agent should create daily note when asked."""
        message = "Can you create my daily note? I worked on the AI project today"

        response = await agent.chat(message)

        # Verify tool was called
        assert mock_github.create_file.called
        call_args = mock_github.create_file.call_args
        assert "Timestamps" in call_args["path"]
        assert "AI project" in call_args["content"]
```

---

## 7. Deployment

### 7.1 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - QDRANT_URL=http://qdrant:6333
      - NEO4J_URL=bolt://neo4j:7687
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://backend:8000

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  # Qdrant and Neo4j are external (HomeLab)

volumes:
  redis_data:
```

### 7.2 GitHub Actions CI

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install poetry
          poetry install
      - name: Run tests
        run: |
          cd backend
          poetry run pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Lint
        run: |
          cd frontend
          npm run lint
      - name: Type check
        run: |
          cd frontend
          npm run type-check
      - name: Test
        run: |
          cd frontend
          npm run test
      - name: Build
        run: |
          cd frontend
          npm run build
```

---

## 8. Security Considerations

### 8.1 API Keys
- All secrets in environment variables
- Never commit `.env` files
- Rotate keys periodically

### 8.2 Authentication
- JWT tokens for web app
- API key for WhatsApp webhook
- Rate limiting on all endpoints

### 8.3 Data Privacy
- Conversations stored encrypted
- Option to delete all data
- No sharing with third parties (except LLM API)

---

## 9. Monitoring & Observability

### 9.1 Logging

```python
# Structured logging with structlog
import structlog

logger = structlog.get_logger()

logger.info(
    "chat_message_processed",
    conversation_id=conv_id,
    message_length=len(message),
    tools_called=["create_daily_note"],
    response_time_ms=150,
    english_errors_found=2,
)
```

### 9.2 Health Checks

```python
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "llm": await check_openrouter(),
            "github": await check_github(),
            "qdrant": await check_qdrant(),
            "neo4j": await check_neo4j(),
        }
    }
```

---

## Next Steps

1. [ ] Review and approve architecture
2. [ ] Create GitHub repository
3. [ ] Setup project scaffolding
4. [ ] Implement first vertical slice (chat without tools)
