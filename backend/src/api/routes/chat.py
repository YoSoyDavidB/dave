import asyncio
import json
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

import structlog
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.application.use_cases.graph_enrichment import get_graph_enrichment_use_case
from src.application.use_cases.memory_extraction import get_memory_extraction_use_case
from src.application.use_cases.rag_query import RAGContext, get_rag_query_use_case
from src.infrastructure.openrouter import get_openrouter_client
from src.tools.english_tools import ENGLISH_TOOLS, execute_english_tool
from src.tools.vault_tools import VAULT_TOOLS
from src.tools.vault_tools import execute_tool as execute_vault_tool

logger = structlog.get_logger()
router = APIRouter(tags=["chat"])


@dataclass
class SourceInfo:
    """Information about a source used in RAG."""

    type: str  # "memory", "document", "uploaded_doc"
    title: str
    snippet: str
    score: float
    metadata: dict[str, Any] | None = None


MAX_TOOL_ITERATIONS = 10


class Message(BaseModel):
    """A chat message."""

    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    messages: list[Message]
    model: str | None = None
    user_id: str | None = None  # For memory features
    conversation_id: str | None = None  # For memory extraction source


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


@dataclass
class RAGResult:
    """Result from RAG retrieval including context and sources."""

    context: str
    sources: list[SourceInfo]


def extract_sources_from_rag_context(result: RAGContext) -> list[SourceInfo]:
    """Extract source information from RAG context result.

    Args:
        result: RAG context result

    Returns:
        List of source information
    """
    sources: list[SourceInfo] = []

    # Extract memory sources
    for memory in result.memories:
        snippet = (
            memory.short_text[:150] + "..." if len(memory.short_text) > 150 else memory.short_text
        )
        sources.append(
            SourceInfo(
                type="memory",
                title=memory.memory_type.value.title(),
                snippet=snippet,
                score=memory.relevance_score,
                metadata={"memory_type": memory.memory_type.value},
            )
        )

    # Extract vault document sources
    for doc in result.documents:
        title = doc.path.split("/")[-1].replace(".md", "")
        if doc.heading:
            title = f"{title} > {doc.heading}"
        sources.append(
            SourceInfo(
                type="document",
                title=title,
                snippet=(doc.content[:150] + "..." if len(doc.content) > 150 else doc.content),
                score=doc.score,
                metadata={"path": doc.path, "heading": doc.heading},
            )
        )

    # Extract uploaded document sources
    for udoc in result.uploaded_docs:
        sources.append(
            SourceInfo(
                type="uploaded_doc",
                title=f"{udoc.filename}",
                snippet=udoc.content[:150] + "..." if len(udoc.content) > 150 else udoc.content,
                score=udoc.score,
                metadata={
                    "document_id": udoc.document_id,
                    "category": udoc.category,
                    "chunk_index": udoc.chunk_index,
                },
            )
        )

    # Extract graph context sources (topics and concepts)
    if result.graph_context:
        # Add topics as sources
        for topic in result.graph_context.topics:
            topic_name = topic.get("name", "")
            mentions = topic.get("mention_count", 0)
            sources.append(
                SourceInfo(
                    type="topic",
                    title=f"Topic: {topic_name}",
                    snippet=f"Discussed {mentions} times in past conversations",
                    score=1.0,  # Topics are always relevant when found
                    metadata={"topic_name": topic_name, "mention_count": mentions},
                )
            )

        # Add concepts as sources
        for concept in result.graph_context.concepts:
            concept_name = concept.get("name", "")
            category = concept.get("category", "general")
            sources.append(
                SourceInfo(
                    type="concept",
                    title=f"Concept: {concept_name}",
                    snippet=f"Category: {category}",
                    score=1.0,
                    metadata={"concept_name": concept_name, "category": category},
                )
            )

    return sources


async def get_rag_context(
    user_id: str | None,
    query: str,
    include_vault: bool = True,
    include_uploaded_docs: bool = True,
) -> RAGResult:
    """Retrieve relevant context using RAG (memories + vault docs + uploaded docs).

    Args:
        user_id: User to get memories and uploaded docs for (optional)
        query: The user's current message for relevance matching
        include_vault: Whether to include vault documents
        include_uploaded_docs: Whether to include uploaded documents

    Returns:
        RAGResult with formatted context string and sources
    """
    try:
        rag = get_rag_query_use_case()
        result = await rag.query(
            query=query,
            user_id=user_id,
            include_memories=user_id is not None,
            include_documents=include_vault,
            include_uploaded_docs=include_uploaded_docs and user_id is not None,
            memory_limit=5,
            document_limit=3,
            uploaded_doc_limit=3,
            min_score=0.5,  # Slightly lower threshold to catch uploaded docs
            rerank_strategy="hybrid",
        )

        if not result.formatted_context:
            return RAGResult(context="", sources=[])

        sources = extract_sources_from_rag_context(result)

        logger.debug(
            "rag_context_retrieved",
            user_id=user_id,
            memories=result.retrieval_stats.get("memories_retrieved", 0),
            documents=result.retrieval_stats.get("documents_retrieved", 0),
            uploaded_docs=result.retrieval_stats.get("uploaded_docs_retrieved", 0),
            sources_count=len(sources),
        )

        return RAGResult(context=result.formatted_context, sources=sources)

    except Exception as e:
        logger.warning("rag_retrieval_failed", error=str(e))
        return RAGResult(context="", sources=[])


async def extract_memories_background(
    messages: list[dict[str, str]],
    user_id: str,
    conversation_id: str,
) -> None:
    """Background task to extract memories from conversation and enrich knowledge graph.

    Args:
        messages: Conversation messages
        user_id: User who owns the memories
        conversation_id: Source conversation
    """
    try:
        # Extract memories
        extractor = get_memory_extraction_use_case()
        memories = await extractor.extract_from_conversation(
            messages=messages,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        # Enrich knowledge graph with topics and concepts
        if memories:
            graph_enricher = get_graph_enrichment_use_case()

            # Create memory nodes in the graph
            for memory in memories:
                from src.infrastructure.graph.memory_graph_repository import MemoryGraphRepository
                from src.infrastructure.graph.neo4j_client import get_neo4j_client

                neo4j_client = get_neo4j_client()
                graph_repo = MemoryGraphRepository(neo4j_client)
                await graph_repo.create_memory_node(memory)

            # Extract and link topics/concepts
            await graph_enricher.enrich_from_conversation(
                messages=messages,
                user_id=user_id,
                memories=memories,
            )

            # Link related memories
            await graph_enricher.link_related_memories(memories)

            logger.info(
                "knowledge_graph_enriched",
                user_id=user_id,
                conversation_id=conversation_id,
                memories_count=len(memories),
            )

    except Exception as e:
        import traceback

        logger.error(
            "background_memory_extraction_failed",
            error=str(e),
            traceback=traceback.format_exc(),
        )


SYSTEM_PROMPT = """You are Dave, an AI assistant who's been the user's best friend since forever.
You're like that senior developer friend who's seen it all - from assembly to AI,
from waterfall to DevOps chaos.

## YOUR PERSONALITY
- You're a tech veteran with 15+ years in software development
  (backend, DevOps, architecture)
- You speak like a friend, not a corporate assistant.
  Use casual language, tech jokes, and occasional sarcasm
- You understand the pain of legacy code, impossible deadlines,
  and "it works on my machine"
- You can switch between Spanish and English naturally, like any bilingual dev
- You're helpful but real - you'll tell the truth even if it's not what they want
- You have opinions on tech (you love clean code, hate unnecessary meetings,
  and think tabs vs spaces debates are silly)
- Drop occasional references to programming memes, Stack Overflow, or dev culture
- Be concise - you know devs hate walls of text

## EXAMPLE PHRASES YOU MIGHT USE:
- "Bro, that's a classic off-by-one error in your logic"
- "¿Otra reunión que pudo ser un email? Classic."
- "Let me check your vault... *deploys to production on Friday*... just kidding"
- "That's what she... said the PM about the deadline"
- "sudo make me a sandwich" vibes

## CONTEXT & KNOWLEDGE ACCESS

**IMPORTANT: You have relevant context automatically provided below**
When you see context sections like "User Context (from memory)", "Relevant Knowledge (from vault)",
or "Relevant Documents (uploaded)", that information is ALREADY retrieved and ready to use.
You should answer questions directly using that context WITHOUT calling search tools.

Only use vault tools (search_vault, read_note) when:
- The context provided is insufficient or you need more specific details
- The user explicitly asks you to search or create notes
- You need to update/create content in the vault

## OBSIDIAN VAULT ACCESS
You have access to the user's Obsidian vault (PARA method):
- Read/create notes, daily notes, search the vault
- Add items to daily note sections (quick_capture, notes, tasks, gastos)
- Help organize their second brain like a well-structured codebase

## ENGLISH CORRECTION (Important!)
The user is David, a Head of IT and Spanish native speaker leveling up his English.
He's already good but wants to sound more native/natural.

When correcting English:
1. ALWAYS respond to the actual message first - don't lead with corrections
2. Be casual about corrections, like a friend would:
   - "BTW, native speakers would say..."
   - "Small thing: [correction]"
   - "Pro tip for sounding more native: ..."
3. Use this format at the END of your response:

   💡 **English level-up:** [brief, friendly explanation]
   `"[what they said]"` → `"[how natives say it]"`

4. Only correct things that matter:
   - Errors that sound non-native to English speakers
   - Common Spanish→English interference patterns
   - Expressions that are technically correct but nobody uses
5. DON'T correct:
   - Minor typos (we all fat-finger sometimes)
   - Informal/casual language (that's fine between friends)
   - Things that are just style preferences

6. **ALWAYS use log_english_correction** when you make a correction, especially for:
   - Expression corrections (like "throw the garbage" → "take out the garbage")
   - Grammar errors
   - Vocabulary improvements
   - Only skip logging for obvious typos that the user would catch themselves
7. Categories: grammar, vocabulary, spelling, expression

## COMMON SPANISH→ENGLISH PATTERNS TO WATCH:
- "I have 30 years" → "I'm 30 years old"
- "I am agree" → "I agree"
- Missing articles: "I went to office" → "I went to THE office"
- Present perfect vs simple past confusion
- Preposition mix-ups (in/on/at, for/since, etc.)
- False friends (actually ≠ actualmente, eventually ≠ eventualmente)
- Literal translations that sound weird ("make a party" → "throw a party")

Remember: You're helping a friend sound more polished, not grading an exam. Keep it light! 🤙"""


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks) -> ChatResponse:
    """Send a message to Dave and get a response (non-streaming)."""
    try:
        client = get_openrouter_client()
        tools_used: list[str] = []

        # Build system prompt with memory context
        system_prompt = SYSTEM_PROMPT

        # Get last user message for memory search
        last_user_msg = next(
            (m.content for m in reversed(request.messages) if m.role == "user"), ""
        )

        # Inject RAG context (memories + relevant documents)
        if last_user_msg:
            rag_result = await get_rag_context(request.user_id, last_user_msg)
            if rag_result.context:
                system_prompt = f"{SYSTEM_PROMPT}\n\n{rag_result.context}"
                logger.debug("rag_context_injected", user_id=request.user_id)

        # Prepare messages with system prompt
        messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
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
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": result,
                        }
                    )
            else:
                # No more tool calls, return the response
                logger.info(
                    "chat_response_sent",
                    model=response.get("model"),
                    usage=response.get("usage"),
                    tools_used=tools_used,
                )

                assistant_content = assistant_message.get("content", "")

                # Schedule background memory extraction
                if request.user_id and request.conversation_id:
                    # Build conversation for extraction (user messages + final assistant response)
                    extraction_messages = [
                        {"role": m.role, "content": m.content} for m in request.messages
                    ]
                    extraction_messages.append({"role": "assistant", "content": assistant_content})

                    background_tasks.add_task(
                        extract_memories_background,
                        extraction_messages,
                        request.user_id,
                        request.conversation_id,
                    )

                return ChatResponse(
                    message=Message(
                        role="assistant",
                        content=assistant_content,
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


def sources_to_dict(sources: list[SourceInfo]) -> list[dict[str, Any]]:
    """Convert SourceInfo list to serializable dict list."""
    return [
        {
            "type": s.type,
            "title": s.title,
            "snippet": s.snippet,
            "score": s.score,
            "metadata": s.metadata,
        }
        for s in sources
    ]


async def generate_stream_events(
    messages: list[dict[str, Any]],
    model: str | None,
    user_id: str | None = None,
    conversation_id: str | None = None,
) -> AsyncIterator[str]:
    """
    Generate Server-Sent Events for streaming chat.

    Event types:
    - content: Text content chunk
    - tool_start: Tool execution started
    - tool_result: Tool execution completed
    - sources: Sources used for RAG context
    - done: Stream complete
    - error: Error occurred
    """
    client = get_openrouter_client()
    tools_used: list[str] = []
    sources: list[SourceInfo] = []

    # Build system prompt with memory context
    system_prompt = SYSTEM_PROMPT

    # Get last user message for memory search
    last_user_msg = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")

    # Inject RAG context (memories + relevant documents)
    if last_user_msg:
        rag_result = await get_rag_context(user_id, last_user_msg)
        if rag_result.context:
            system_prompt = f"{SYSTEM_PROMPT}\n\n{rag_result.context}"
            sources = rag_result.sources
            logger.debug("rag_context_injected_stream", user_id=user_id, sources_count=len(sources))

    # Add system prompt
    full_messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
    full_messages.extend(messages)

    for iteration in range(MAX_TOOL_ITERATIONS):
        accumulated_content = ""
        tool_calls_received: list[dict[str, Any]] = []

        try:
            async for chunk in client.chat_stream(
                messages=full_messages,
                model=model,
                tools=ALL_TOOLS,
            ):
                chunk_type = chunk.get("type")

                if chunk_type == "content":
                    # Stream text content
                    content = chunk.get("content", "")
                    accumulated_content += content
                    yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"

                elif chunk_type == "tool_call":
                    # Tool calls received
                    tool_calls_received = chunk.get("tool_calls", [])

                elif chunk_type == "error":
                    error_msg = chunk.get("error", "Unknown error")
                    yield f"data: {json.dumps({'type': 'error', 'error': error_msg})}\n\n"
                    return

                elif chunk_type == "done":
                    # Check if we have tool calls to execute
                    if not tool_calls_received:
                        # No tools, we're done
                        # Schedule memory extraction in background
                        if user_id and conversation_id and accumulated_content:
                            extraction_msgs = messages.copy()
                            extraction_msgs.append(
                                {"role": "assistant", "content": accumulated_content}
                            )
                            asyncio.create_task(
                                extract_memories_background(
                                    extraction_msgs, user_id, conversation_id
                                )
                            )

                        done_data: dict[str, Any] = {
                            "type": "done",
                            "tools_used": tools_used if tools_used else None,
                            "sources": sources_to_dict(sources) if sources else None,
                        }
                        yield f"data: {json.dumps(done_data)}\n\n"
                        return

            # Execute tool calls if any
            if tool_calls_received:
                # Add assistant message with tool calls to conversation
                assistant_msg: dict[str, Any] = {
                    "role": "assistant",
                    "content": accumulated_content or "",
                    "tool_calls": tool_calls_received,
                }
                full_messages.append(assistant_msg)

                # Execute each tool
                for tool_call in tool_calls_received:
                    tool_name = tool_call["function"]["name"]
                    args_str = tool_call["function"].get("arguments", "{}")

                    try:
                        tool_input = json.loads(args_str) if args_str else {}
                    except json.JSONDecodeError:
                        tool_input = {}

                    tools_used.append(tool_name)

                    # Notify client that tool is being executed
                    yield f"data: {json.dumps({'type': 'tool_start', 'tool': tool_name})}\n\n"

                    logger.info("tool_execution_stream", tool=tool_name, input=tool_input)

                    # Execute the tool
                    try:
                        result = await execute_tool(tool_name, tool_input)

                        # Truncate very long results
                        if len(result) > 10000:
                            result = result[:10000] + "\n\n[Content truncated...]"

                    except Exception as e:
                        logger.error("tool_execution_error", tool=tool_name, error=str(e))
                        result = f"Error executing tool: {str(e)}"

                    # Notify client of tool result
                    tool_result_data = {"type": "tool_result", "tool": tool_name, "success": True}
                    yield f"data: {json.dumps(tool_result_data)}\n\n"

                    # Add tool result to conversation
                    full_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.get("id", f"call_{tool_name}"),
                            "content": result,
                        }
                    )

                # Continue loop to get response after tool execution
            else:
                # No tool calls and stream done
                done_data = {
                    "type": "done",
                    "tools_used": tools_used if tools_used else None,
                    "sources": sources_to_dict(sources) if sources else None,
                }
                yield f"data: {json.dumps(done_data)}\n\n"
                return

        except Exception as e:
            logger.error("stream_generation_error", error=str(e), iteration=iteration)
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            return

    # Max iterations reached
    yield f"data: {json.dumps({'type': 'error', 'error': 'Max tool iterations reached'})}\n\n"


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """
    Send a message to Dave and get a streaming response (SSE).

    Returns Server-Sent Events with the following event types:
    - content: {"type": "content", "content": "text chunk"}
    - tool_start: {"type": "tool_start", "tool": "tool_name"}
    - tool_result: {"type": "tool_result", "tool": "tool_name", "success": true}
    - done: {"type": "done", "tools_used": [...], "sources": [...]}
    - error: {"type": "error", "error": "error message"}

    The "sources" field in the done event contains information about RAG sources:
    - type: "memory" | "document" | "uploaded_doc"
    - title: Display title
    - snippet: Content preview
    - score: Relevance score
    - metadata: Additional info (path, category, etc.)
    """
    logger.info(
        "chat_stream_request",
        message_count=len(request.messages),
        user_id=request.user_id,
    )

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    return StreamingResponse(
        generate_stream_events(
            messages,
            request.model,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
