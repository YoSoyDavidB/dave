---
created: 2024-11-22
last_updated: 2025-11-23
last_reviewed: 2025-11-23
tags:
  - project
  - AI
  - planning
status: active
---

# 📅 Dave - Development Plan

> **Status Update (Nov 23, 2025):** Phases 1-3 are COMPLETE including frontend. Authentication system implemented. Currently preparing for Phase 4 (Smart Dave with memory).

---

## ✅ Phase 1: Foundation (Semanas 1-3) - COMPLETE

### Sprint 1.1: Project Setup (Semana 1)
**Status: COMPLETE.** El proyecto está configurado con backend (FastAPI), frontend (React), Docker y CI/CD básicos.

### Sprint 1.2: LLM Integration (Semana 2)
**Status: COMPLETE.** El cliente de OpenRouter está implementado. El endpoint de chat y una UI de chat básica existen y son funcionales.

### Sprint 1.3: Streaming + WebSocket (Semana 3)
**Status: COMPLETE.** Las respuestas en streaming (SSE) están implementadas tanto en el backend como en el frontend.

---

## ✅ Phase 2: English Correction (Semanas 4-5) - COMPLETE

### Sprint 2.1: English Analyzer (Semana 4)
**Status: COMPLETE.** La lógica para analizar los mensajes del usuario está implementada en el backend a través de herramientas.

### Sprint 2.2: Corrections Display (Semana 5)
**Status: COMPLETE.**
- Backend: API endpoints para correcciones (`/api/v1/english/*`)
- Frontend: Página `/learn` con dashboard de progreso
- Estadísticas por categoría (grammar, vocabulary, spelling, expression)
- Lista filtrable de correcciones con explicaciones

---

## ✅ Phase 3: Obsidian Integration (Semanas 6-8) - COMPLETE

### Sprint 3.1: GitHub Integration (Semana 6)
**Status: COMPLETE.** El cliente de GitHub (`GitHubVaultClient`) está implementado y probado.

### Sprint 3.2: Create Daily Note (Semana 7)
**Status: COMPLETE.**
- Tool `create_daily_note` que lee la plantilla del vault y procesa sintaxis Templater
- Tool `append_to_daily_note` con auto-creación si no existe
- Secciones soportadas: quick_capture, notes, tasks, gastos, english

### Sprint 3.3: More Tools + UI (Semana 8)
**Status: COMPLETE.**
- Frontend: Página `/vault` con navegador de archivos
- Búsqueda de notas, navegación por carpetas
- Visor de markdown integrado
- Indicadores visuales de herramientas en el chat

---

## 🚧 Phase 4: Smart Dave - Memory & RAG (Semanas 9-11) - IN PROGRESS

> **Reference:** Arquitectura inspirada en proyecto AION (`/Users/davidbuitrago/Documents/AION`)

### Sprint 4.1: Infrastructure Setup (Semana 9)
**Goal:** Configurar Qdrant y servicios base de embeddings

#### User Stories
- **US-4.1.1**: Como desarrollador, necesito un cliente Qdrant configurado para almacenar vectores
- **US-4.1.2**: Como desarrollador, necesito un servicio de embeddings que convierta texto a vectores
- **US-4.1.3**: Como desarrollador, necesito colecciones separadas para memorias y documentos

| Task | Description | Priority |
|------|-------------|----------|
| Qdrant client wrapper | Cliente async con manejo de conexiones y errores | P0 |
| Embedding service | Usar OpenRouter para text-embedding-3-small (1536 dims) | P0 |
| Collection setup | Crear colecciones `memories` y `kb_documents` | P0 |
| Docker config | Agregar Qdrant a docker-compose | P0 |
| Tests unitarios | Tests para cliente Qdrant y embeddings | P0 |

**Deliverables:**
- `src/infrastructure/vector_store/qdrant_client.py`
- `src/infrastructure/embeddings/embedding_service.py`
- Qdrant corriendo en Docker (puerto 6333)
- Tests pasando

---

### Sprint 4.2: Long-Term Memory System (Semana 10)
**Goal:** Dave extrae y recuerda preferencias del usuario automáticamente

#### User Stories
- **US-4.2.1**: Como usuario, quiero que Dave recuerde mis preferencias sin que yo las tenga que repetir
- **US-4.2.2**: Como usuario, quiero que Dave aprenda hechos sobre mí de forma natural durante las conversaciones
- **US-4.2.3**: Como usuario, quiero que las memorias obsoletas se eliminen automáticamente

#### Memory Entity Model
```python
class Memory:
    memory_id: UUID
    user_id: str
    short_text: str                    # Contenido (max 500 chars)
    memory_type: MemoryType            # PREFERENCE, FACT, TASK, GOAL, PROFILE
    timestamp: datetime
    last_referenced_at: datetime
    relevance_score: float             # 0-1, decae con el tiempo
    num_times_referenced: int
    embedding: list[float]             # Vector 1536 dims
    source: str                        # conversation_id o file path
```

#### Memory Types
| Type | Description | Example |
|------|-------------|---------|
| PREFERENCE | Preferencias del usuario | "Prefiere respuestas concisas" |
| FACT | Información factual | "Es ingeniero de software" |
| TASK | Tareas pendientes | "Quiere aprender Rust" |
| GOAL | Metas a largo plazo | "Está construyendo un startup" |
| PROFILE | Info de perfil | "Se llama David" |

| Task | Description | Priority |
|------|-------------|----------|
| Memory entity | Definir modelo en `domain/entities/memory.py` | P0 |
| Memory repository | Interface + implementación Qdrant | P0 |
| Memory extraction | Extraer memorias de conversaciones con LLM | P0 |
| Background extraction | Ejecutar extracción en background después del chat | P0 |
| Relevance decay | Sistema de decaimiento (factor 0.95) | P1 |
| Memory consolidation | Eliminar memorias obsoletas (90 días sin uso) | P1 |
| Tests | Tests para extracción y búsqueda | P0 |

**Deliverables:**
- `src/domain/entities/memory.py`
- `src/infrastructure/vector_store/memory_repository.py`
- `src/application/use_cases/memory_extraction.py`
- Memorias se extraen automáticamente de cada conversación
- Dave usa memorias relevantes en sus respuestas

---

### Sprint 4.3: RAG Pipeline (Semana 11)
**Goal:** Búsqueda semántica sobre vault y memorias con contexto inteligente

#### User Stories
- **US-4.3.1**: Como usuario, quiero preguntar "¿Qué escribí sobre X?" y obtener resultados relevantes
- **US-4.3.2**: Como usuario, quiero que Dave use información de mi vault para responder preguntas
- **US-4.3.3**: Como usuario, quiero ver las fuentes que Dave usó para su respuesta

#### RAG Pipeline Flow
```
User Query
    ↓
1. Generate query embedding
    ↓
2. Search relevant context:
   ├─ Memories (Qdrant) → filtered by user_id
   ├─ Documents (Qdrant) → vault chunks
   └─ (Future: Neo4j entities)
    ↓
3. Rerank results (hybrid: keyword + recency)
    ↓
4. Assemble context text (markdown format)
    ↓
5. Generate response with context
    ↓
6. Return answer + sources used
```

| Task | Description | Priority |
|------|-------------|----------|
| Document chunking | Dividir notas del vault en chunks (500 tokens) | P0 |
| Vault indexing | Indexar vault completo en Qdrant | P0 |
| RAG use case | Pipeline de retrieval + generation | P0 |
| Result reranker | Estrategias: MMR, keyword boost, recency, hybrid | P1 |
| Context assembly | Formatear contexto como markdown | P0 |
| Incremental sync | Solo indexar archivos nuevos/modificados | P1 |
| Sources UI | Mostrar fuentes en el frontend | P1 |
| Tests | Tests para RAG pipeline | P0 |

**Deliverables:**
- `src/infrastructure/vector_store/document_repository.py`
- `src/application/use_cases/rag_use_case.py`
- `src/infrastructure/vector_store/result_reranker.py`
- Vault indexado en Qdrant
- Chat responde con contexto del vault
- UI muestra sources usados

---

## Phase 5: Proactive Features (Semanas 11-12)

(No changes, remains as future work)

---

## Phase 6: Polish & Deploy (Semanas 13-14)

(No changes, remains as future work)

---

## Milestones

### ✅ 🏁 M1: First Conversation (Week 3)
- [x] Chat funciona end-to-end
- [x] Personalidad de Dave definida
- [x] Streaming works

### ✅ 🏁 M2: English Dave (Week 5)
- [x] Correcciones funcionan (backend)
- [x] Feedback amigable (frontend `/learn`)
- [x] Errores se trackean

### ✅ 🏁 M3: Obsidian Connected (Week 8)
- [x] Daily notes desde chat (con plantilla del vault)
- [x] Append to daily note (auto-create)
- [x] Basic search (backend + frontend `/vault`)
- [x] Vault browser UI

### ✅ 🏁 M3.5: Authentication (Added)
- [x] User registration/login
- [x] JWT cookies authentication
- [x] Protected routes
- [x] Auth UI matching app design

### ➡️ 🏁 M4: Smart Dave (Weeks 9-11)
- [ ] Qdrant + Embedding service configurados
- [ ] Sistema de memoria a largo plazo
  - [ ] Extracción automática de preferencias/hechos
  - [ ] Búsqueda semántica de memorias
  - [ ] Decay y consolidación de memorias
- [ ] RAG Pipeline
  - [ ] Vault indexado y chunkeado
  - [ ] Búsqueda semántica sobre vault
  - [ ] Context assembly con sources
- [ ] UI muestra fuentes usadas

### 🏁 M5: MVP Complete (Week 14)
- [ ] Proactive reminders
- [ ] Progress dashboard
- [ ] Deployed to production
- [x] Documentation complete

---

## Current Architecture

### Backend (FastAPI)
- **API Routes**: `/api/v1/` prefix
  - `chat.py` - Chat con streaming SSE
  - `conversations.py` - CRUD conversaciones
  - `vault.py` - Operaciones del vault
  - `english.py` - Estadísticas y correcciones
  - `auth.py` - Autenticación JWT
  - `health.py` - Health check

- **Tools**:
  - Vault: `read_note`, `read_daily_note`, `create_note`, `create_daily_note`, `list_directory`, `search_vault`, `append_to_daily_note`
  - English: `log_english_correction`, `get_english_progress`, `get_recent_english_errors`

- **Infrastructure**:
  - `github_vault.py` - Cliente GitHub API
  - `database.py` - PostgreSQL async
  - `openrouter.py` - Cliente LLM

### Frontend (React + TypeScript)
- **Pages**: Chat (`/`), EnglishProgress (`/learn`), VaultBrowser (`/vault`), Dashboard (`/dashboard`), Login, Register
- **Stores**: `chatStore.ts`, `authStore.ts` (Zustand)
- **Design System**: Ver `UI-Guidelines.md`

### Docker Services
- `backend` - FastAPI (puerto 8000)
- `frontend` - Nginx serving React (puerto 5173)
- `redis` - Cache
- `postgres` - Database (puerto 5432)
- `qdrant` - Vector database (puerto 6333) - **NEW**

---

## Memory & RAG Architecture (Phase 4)

### Data Flow Diagram
```
User Message
     ↓
  ChatUseCase
     ├─ 1. RAG Pipeline (sync)
     │    ├─ Generate query embedding
     │    ├─ Search memories (Qdrant)
     │    ├─ Search documents (Qdrant)
     │    ├─ Rerank results
     │    ├─ Assemble context
     │    └─ Generate response with LLM
     │
     └─ 2. Background Extraction (async)
          ├─ Extract memories from conversation
          │    ├─ LLM identifies preferences/facts
          │    ├─ Generate embeddings
          │    └─ Store in Qdrant
          └─ (Future: Extract entities → Neo4j)
```

### Vector Store Collections
| Collection | Content | Vector Size | Payload |
|------------|---------|-------------|---------|
| `memories` | User preferences, facts, goals | 1536 | user_id, type, relevance_score, timestamp |
| `kb_documents` | Vault chunks | 1536 | path, title, chunk_index, last_modified |

### Memory Lifecycle
```
1. CREATION
   User says something → LLM extracts memory → Embed → Store

2. RETRIEVAL
   User asks question → Embed query → Search similar → Inject in context

3. MAINTENANCE
   - Referenced: boost relevance (+0.1)
   - Time passes: decay relevance (×0.95)
   - 90 days unused: delete
```

### Key Interfaces
```python
# Memory Repository Interface
class IMemoryRepository(Protocol):
    async def create(memory: Memory) -> Memory
    async def search_similar(
        query_embedding: list[float],
        user_id: str,
        limit: int = 5,
        min_score: float = 0.7
    ) -> list[tuple[Memory, float]]
    async def update_relevance(memory_id: UUID, boost: float)
    async def delete_stale(days: int = 90) -> int

# Document Repository Interface
class IDocumentRepository(Protocol):
    async def index_document(path: str, chunks: list[str])
    async def search_similar(
        query_embedding: list[float],
        limit: int = 10
    ) -> list[tuple[DocumentChunk, float]]
    async def delete_by_path(path: str)

# Embedding Service Interface
class IEmbeddingService(Protocol):
    async def embed_text(text: str) -> list[float]
    async def embed_texts(texts: list[str]) -> list[list[float]]
```

### File Structure (Phase 4)
```
backend/src/
├── domain/
│   └── entities/
│       └── memory.py          # Memory, MemoryType enums
├── infrastructure/
│   ├── vector_store/
│   │   ├── qdrant_client.py   # Qdrant wrapper
│   │   ├── memory_repository.py
│   │   ├── document_repository.py
│   │   └── result_reranker.py
│   └── embeddings/
│       └── embedding_service.py
└── application/
    └── use_cases/
        ├── rag_use_case.py
        └── memory_extraction.py
```
