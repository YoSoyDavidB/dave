---
created: 2024-11-22
tags:
  - project
  - AI
  - planning
status: draft
---

# 📅 Dave - Development Plan

> Tiempo estimado: 5-10 horas/semana
> Duración total: ~14 semanas para MVP completo

---

## Phase 1: Foundation (Semanas 1-3)

### Sprint 1.1: Project Setup (Semana 1)
**Goal:** Tener el proyecto configurado y un "Hello World" funcionando

| Task | Estimated Hours | Priority |
|------|-----------------|----------|
| Crear repositorio GitHub | 0.5h | P0 |
| Setup backend (FastAPI + Poetry) | 2h | P0 |
| Setup frontend (React + Vite + TypeScript) | 2h | P0 |
| Docker Compose básico | 1h | P0 |
| CI/CD con GitHub Actions | 2h | P1 |
| Configurar pytest + primera test | 1h | P0 |
| **Total** | **8.5h** | |

**Deliverable:**
- Proyecto corriendo en local con `docker-compose up`
- Endpoint `/health` funcionando
- Tests corriendo en CI

---

### Sprint 1.2: LLM Integration (Semana 2)
**Goal:** Tener una conversación básica con el LLM

| Task | Estimated Hours | Priority |
|------|-----------------|----------|
| OpenRouter client (con retry, timeout) | 3h | P0 |
| Endpoint POST /api/chat básico | 2h | P0 |
| Tests para LLM client (mocking) | 2h | P0 |
| System prompt inicial (personalidad) | 1h | P0 |
| Frontend: Chat UI básico | 3h | P0 |
| **Total** | **11h** | |

**Deliverable:**
- Puedo enviar un mensaje y recibir respuesta de Dave
- UI básica tipo chat
- Personalidad de "amigo cercano" funciona

---

### Sprint 1.3: Streaming + WebSocket (Semana 3)
**Goal:** Respuestas en streaming como ChatGPT

| Task | Estimated Hours | Priority |
|------|-----------------|----------|
| Implementar SSE/WebSocket en backend | 3h | P0 |
| Streaming en frontend | 2h | P0 |
| Typing indicator | 1h | P1 |
| Manejo de errores y reconexión | 2h | P1 |
| Tests de streaming | 2h | P1 |
| **Total** | **10h** | |

**Deliverable:**
- Respuestas aparecen palabra por palabra
- Indicador de "Dave is typing..."
- Manejo graceful de errores de conexión

---

## Phase 2: English Correction (Semanas 4-5)

### Sprint 2.1: English Analyzer (Semana 4)
**Goal:** Detectar errores de inglés en mensajes del usuario

| Task | Estimated Hours | Priority |
|------|-----------------|----------|
| EnglishAnalyzer class | 3h | P0 |
| Prompt engineering para análisis | 2h | P0 |
| Modelo de datos para errores | 1h | P0 |
| Tests con casos reales | 2h | P0 |
| Integrar análisis en chat flow | 2h | P0 |
| **Total** | **10h** | |

**Deliverable:**
- Cada mensaje del usuario es analizado
- Se detectan errores de gramática y naturalidad
- Análisis no bloquea el flujo principal

---

### Sprint 2.2: Corrections Display (Semana 5)
**Goal:** Mostrar correcciones de manera amigable

| Task | Estimated Hours | Priority |
|------|-----------------|----------|
| EnglishCorrector: genera correcciones amigables | 2h | P0 |
| Formato de corrección en respuesta | 1h | P0 |
| UI component para correcciones | 2h | P0 |
| Persistir correcciones en DB | 2h | P1 |
| Tests de corrector | 2h | P0 |
| **Total** | **9h** | |

**Deliverable:**
- Correcciones aparecen al final del mensaje
- Formato: "💡 English tip: [corrección]"
- Correcciones guardadas para tracking

---

## Phase 3: Obsidian Integration (Semanas 6-8)

### Sprint 3.1: GitHub Integration (Semana 6)
**Goal:** Conectar con el vault via GitHub API

| Task | Estimated Hours | Priority |
|------|-----------------|----------|
| GitHub client (auth, CRUD files) | 3h | P0 |
| Tests de integración con GitHub | 2h | P0 |
| Leer estructura del vault | 2h | P0 |
| Tool framework (base class) | 2h | P0 |
| **Total** | **9h** | |

**Deliverable:**
- Puedo leer/escribir archivos en el repo del vault
- Tests pasan con repo de staging
- Framework para crear tools

---

### Sprint 3.2: Create Daily Note (Semana 7)
**Goal:** Crear daily notes desde el chat

| Task | Estimated Hours | Priority |
|------|-----------------|----------|
| CreateDailyNote tool | 3h | P0 |
| Parsear template de Daily Note | 2h | P0 |
| Extraer info de conversación para note | 2h | P0 |
| Integrar tool con agent | 2h | P0 |
| Tests E2E | 2h | P0 |
| **Total** | **11h** | |

**Deliverable:**
- "Create my daily note" funciona
- Nota se crea con formato correcto
- Se extrae info relevante de la conversación

---

### Sprint 3.3: More Tools (Semana 8)
**Goal:** Person notes, tasks, search

| Task | Estimated Hours | Priority |
|------|-----------------|----------|
| CreatePersonNote tool | 2h | P1 |
| AddTask tool | 2h | P1 |
| SearchNotes tool (keyword) | 2h | P1 |
| Tool selection logic | 2h | P0 |
| Tests para cada tool | 2h | P0 |
| **Total** | **10h** | |

**Deliverable:**
- Puedo crear notas de personas
- Puedo agregar tasks desde chat
- Búsqueda básica funciona

---

## Phase 4: Memory & RAG (Semanas 9-10)

### Sprint 4.1: Conversation Memory (Semana 9)
**Goal:** Dave recuerda conversaciones anteriores

| Task | Estimated Hours | Priority |
|------|-----------------|----------|
| Qdrant client setup | 2h | P0 |
| Embedding service | 2h | P0 |
| Store/retrieve conversation history | 3h | P0 |
| Context injection en prompts | 2h | P0 |
| Tests de memoria | 2h | P0 |
| **Total** | **11h** | |

**Deliverable:**
- Conversaciones se guardan en Qdrant
- Dave puede referenciar conversaciones anteriores
- Contexto relevante se inyecta automáticamente

---

### Sprint 4.2: Vault RAG (Semana 10)
**Goal:** Búsqueda semántica sobre el vault

| Task | Estimated Hours | Priority |
|------|-----------------|----------|
| Indexar vault en Qdrant | 3h | P0 |
| SearchNotes con RAG | 3h | P0 |
| Incremental indexing | 2h | P1 |
| UI para mostrar sources | 1h | P1 |
| Tests de RAG | 2h | P0 |
| **Total** | **11h** | |

**Deliverable:**
- "What did I write about X?" funciona
- Resultados incluyen excerpts relevantes
- Indexing se actualiza automáticamente

---

## Phase 5: Proactive Features (Semanas 11-12)

### Sprint 5.1: Reminders (Semana 11)
**Goal:** Recordatorios proactivos

| Task | Estimated Hours | Priority |
|------|-----------------|----------|
| Task queue setup (Celery + Redis) | 2h | P0 |
| Scan vault for pending tasks | 2h | P0 |
| Reminder notification system | 2h | P0 |
| Weekly review scheduler | 2h | P1 |
| Tests de scheduling | 2h | P0 |
| **Total** | **10h** | |

**Deliverable:**
- Dave me recuerda tareas pendientes
- Weekly review prompt los domingos
- Notificaciones no intrusivas

---

### Sprint 5.2: English Progress Dashboard (Semana 12)
**Goal:** Ver mi progreso en inglés

| Task | Estimated Hours | Priority |
|------|-----------------|----------|
| Stats API endpoint | 2h | P1 |
| Dashboard page (frontend) | 4h | P1 |
| Charts de progreso | 2h | P2 |
| Common errors view | 2h | P1 |
| **Total** | **10h** | |

**Deliverable:**
- Dashboard muestra estadísticas
- Puedo ver mis errores más comunes
- Streak visible

---

## Phase 6: Polish & Deploy (Semanas 13-14)

### Sprint 6.1: Hardening (Semana 13)
**Goal:** Estabilidad y seguridad

| Task | Estimated Hours | Priority |
|------|-----------------|----------|
| Auth system (JWT) | 3h | P0 |
| Rate limiting | 1h | P1 |
| Error handling global | 2h | P0 |
| Logging & monitoring | 2h | P1 |
| Security review | 2h | P0 |
| **Total** | **10h** | |

---

### Sprint 6.2: Production Deploy (Semana 14)
**Goal:** Running en VPS

| Task | Estimated Hours | Priority |
|------|-----------------|----------|
| Production Docker config | 2h | P0 |
| Deploy a Hostinger VPS | 3h | P0 |
| SSL/HTTPS setup | 1h | P0 |
| Domain config | 1h | P1 |
| Smoke testing | 2h | P0 |
| Documentación | 2h | P1 |
| **Total** | **11h** | |

---

## Summary

| Phase | Weeks | Total Hours | Focus |
|-------|-------|-------------|-------|
| 1. Foundation | 1-3 | ~30h | Setup, LLM, Streaming |
| 2. English | 4-5 | ~19h | Analyzer, Corrections |
| 3. Obsidian | 6-8 | ~30h | GitHub, Tools |
| 4. Memory | 9-10 | ~22h | Qdrant, RAG |
| 5. Proactive | 11-12 | ~20h | Reminders, Dashboard |
| 6. Deploy | 13-14 | ~21h | Auth, Deploy |
| **Total** | **14 weeks** | **~142h** | |

**At 7.5h/week average = ~19 weeks**
**At 10h/week = ~14 weeks**

---

## Milestones

### 🏁 M1: First Conversation (Week 3)
- [ ] Chat funciona end-to-end
- [ ] Personalidad de Dave definida
- [ ] Streaming works

### 🏁 M2: English Dave (Week 5)
- [ ] Correcciones funcionan
- [ ] Feedback amigable
- [ ] Errores se trackean

### 🏁 M3: Obsidian Connected (Week 8)
- [ ] Daily notes desde chat
- [ ] People notes
- [ ] Task extraction
- [ ] Basic search

### 🏁 M4: Smart Dave (Week 10)
- [ ] Memoria de conversaciones
- [ ] RAG sobre vault
- [ ] Contexto inteligente

### 🏁 M5: MVP Complete (Week 14)
- [ ] Proactive reminders
- [ ] Progress dashboard
- [ ] Deployed to production
- [ ] Documentation complete

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Scope creep | Stick to MVP features, defer Phase 2 items |
| GitHub API limits | Cache vault locally, batch operations |
| LLM costs | Use cheaper models for analysis, caching |
| Time constraints | Prioritize P0 items, cut P2 if needed |
| Sync conflicts | Wait for GitHub sync, use atomic operations |

---

## Getting Started Checklist

**Week 1 - Day 1:**
- [ ] Create GitHub repo: `Dave-ai`
- [ ] Clone and setup local environment
- [ ] Run first test

**Tools needed:**
- [ ] GitHub account with token
- [ ] OpenRouter API key
- [ ] Docker Desktop
- [ ] VS Code / Cursor
- [ ] Python 3.11+
- [ ] Node.js 20+

**First command:**
```bash
# Clone template
git clone https://github.com/YOUR_USERNAME/Dave-ai.git
cd Dave-ai

# Setup backend
cd backend
poetry install
poetry run pytest

# Setup frontend
cd ../frontend
npm install
npm run dev
```

---

## Next Actions

1. [ ] Review this plan
2. [ ] Create GitHub repository
3. [ ] Start Sprint 1.1
