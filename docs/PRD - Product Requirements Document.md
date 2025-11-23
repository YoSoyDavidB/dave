---
created: 2024-11-22
tags:
  - project
  - AI
  - english
  - PRD
status: draft
version: 0.1
---

# 🤖 Dave - Product Requirements Document

> **Dave**: Tu amigo AI que te ayuda a organizar tu vida mientras mejoras tu inglés.

---

## 1. Visión del Producto

### 1.1 Problem Statement

David (y muchos profesionales no nativos de inglés) enfrenta dos problemas:

1. **Productividad fragmentada**: Tiene un sistema de notas en Obsidian pero la fricción de crear notas, gestionar tareas y mantener el sistema organizado hace que a veces no capture información importante.

2. **Práctica de inglés inconsistente**: Quiere mejorar su inglés escrito pero no tiene un contexto natural y cotidiano donde practicarlo con feedback inmediato.

### 1.2 Solution

**Dave** es un agente conversacional que:
- Actúa como un amigo cercano que te ayuda a gestionar tu vida
- Crea y organiza notas en Obsidian automáticamente
- Te corrige el inglés de manera sutil y natural durante la conversación
- Aprende tus patrones y preferencias con el tiempo

### 1.3 Value Proposition

> "Organiza tu vida conversando con un amigo que además te ayuda a mejorar tu inglés."

**Para el usuario**:
- Reducción de fricción para capturar información
- Práctica de inglés contextualizada y diaria
- Asistente personal que conoce tu vida y contexto

**Diferenciadores**:
- Integración profunda con Obsidian (no solo notas, sino el sistema PARA completo)
- Corrección de inglés sutil e integrada (no es una app de idiomas)
- Personalidad memorable y cercana

---

## 2. Usuarios Objetivo

### 2.1 Persona Principal

**David** - Developer, 30s, Spanish native speaker
- Usa Obsidian para productividad personal y profesional
- Nivel de inglés intermedio-avanzado, quiere sonar más natural
- Poco tiempo, necesita eficiencia
- Aprecia el humor y la interacción cercana

### 2.2 Personas Secundarias (futuro)

- Profesionales que usan Obsidian y quieren mejorar inglés
- Estudiantes de inglés que buscan práctica contextualizada
- Knowledge workers que necesitan un asistente personal

---

## 3. Funcionalidades

### 3.1 Core Features (MVP)

#### F1: Conversación Natural
- Chat tipo WhatsApp/Messenger
- Personalidad definida: amigo cercano, humor, tono burlón amigable
- Memoria de conversaciones anteriores
- Respuestas en inglés (con opción de español si el usuario lo necesita)

#### F2: Gestión de Obsidian Vault
- **Crear Daily Notes**: A partir de la conversación
- **Crear notas de personas**: Cuando mencione gente nueva
- **Agregar tareas**: Extraer TODOs de la conversación
- **Buscar información**: RAG sobre el vault existente
- **Organización PARA**: Colocar notas en el lugar correcto automáticamente

#### F3: Corrección de Inglés
- Análisis de cada mensaje del usuario
- Correcciones al final del mensaje (no inline)
- Tres niveles:
  1. Errores gramaticales
  2. Sugerencias para sonar más natural
  3. Explicaciones breves de por qué
- Tracking de errores frecuentes y progreso

#### F4: Recordatorios y Proactividad
- Recordar tareas pendientes
- Sugerir Weekly Review
- Notificaciones de seguimiento

### 3.2 Features Fase 2

#### F5: Integración con Calendarios
- Google Calendar
- Outlook Calendar
- Crear/modificar eventos desde chat

#### F6: Gestión de Emails
- Leer resúmenes de emails
- Generar drafts de respuestas
- Gmail y Outlook

#### F7: Base de Conocimiento Personal (RAG)
- Subir documentos (manuales, facturas, docs técnicos)
- Búsqueda semántica sobre documentos
- Respuestas contextualizadas

#### F8: Integración WhatsApp
- Bot de WhatsApp como interfaz alternativa
- Misma funcionalidad que web app

### 3.3 Features Fase 3

#### F9: Voice Interface
- Entrada por voz
- Respuestas por voz (TTS)
- Práctica de pronunciación

#### F10: Analytics y Dashboard
- Estadísticas de uso
- Progreso en inglés
- Errores más comunes
- Streak de práctica

---

## 4. Requisitos No Funcionales

### 4.1 Performance
- Respuesta < 3 segundos para mensajes simples
- Respuesta < 10 segundos para operaciones complejas (RAG, múltiples tools)
- Disponibilidad 99% (es herramienta personal, no crítica)

### 4.2 Seguridad
- Datos almacenados de forma segura
- API keys encriptadas
- Autenticación para acceso web
- Datos personales no compartidos con terceros

### 4.3 Escalabilidad
- Inicialmente single-user
- Arquitectura preparada para multi-tenant (futuro)

### 4.4 Mantenibilidad
- Código con tests (TDD)
- Documentación de arquitectura
- Logging estructurado
- Health checks

---

## 5. Personalidad del Agente

### 5.1 Nombre
**Dave** (o alternativas: Mate, Pal, Coach)

### 5.2 Características de Personalidad
- **Cercano**: Habla como un amigo de toda la vida
- **Humorístico**: Usa humor, bromas ligeras, tono burlón amigable
- **Directo**: No da vueltas, va al grano
- **Supportive**: Celebra logros, anima cuando hay dificultades
- **Curioso**: Hace preguntas de seguimiento, muestra interés genuino

### 5.3 Ejemplos de Tono

**Usuario**: "I have a meeting tomorrow with my boss"

**Dave** (mal ejemplo - muy formal):
> "I have noted your meeting. Would you like me to create a calendar event?"

**Dave** (buen ejemplo):
> "Ooh, boss meeting! 😬 What's the occasion - good news or 'we need to talk' vibes? Want me to block some time in your calendar so you can prep?"

**Corrección de inglés** (ejemplo):
> "By the way, quick English tip: instead of 'I have a meeting tomorrow' you could say 'I've got a meeting tomorrow' - sounds more natural in casual conversation. Both are correct though! 👍"

### 5.4 System Prompt Base

```
You are Dave, a friendly AI assistant who helps David organize his life while helping him improve his English.

PERSONALITY:
- You're David's close friend who happens to be really good at organization
- Use casual language, humor, and occasional playful teasing
- Be direct and efficient - David is busy
- Show genuine interest in his life and projects
- Celebrate wins, support during struggles

ENGLISH CORRECTION:
- Always respond in English
- At the end of your response, if David made English mistakes, add a friendly correction
- Format: "💡 English tip: [correction + brief explanation]"
- Focus on: grammar errors, unnatural phrasing, better alternatives
- Keep it light - never make him feel bad about mistakes
- Track patterns: if he repeats the same mistake, mention it

OBSIDIAN INTEGRATION:
- You can create and search notes in David's Obsidian vault
- Follow the PARA method: Projects, Areas, Resources, Archive
- When creating notes, use the appropriate templates
- Daily notes go in Timestamps/YYYY/MM-Month/
- Always confirm before creating/modifying notes

CONTEXT:
- David is a developer working at Qualitas
- He's learning English and taking the New Sound course
- He's in therapy and does "autoregistros"
- He values productivity and organization
- His vault is synced with GitHub every 5 minutes
```

---

## 6. Stack Tecnológico

### 6.1 Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **LLM**: OpenRouter (Claude/GPT-4 via API)
- **Vector DB**: Qdrant (ya desplegado en HomeLab)
- **Graph DB**: Neo4j (ya desplegado en HomeLab) - para relaciones entre entidades
- **Task Queue**: Celery + Redis (para tareas async)

### 6.2 Frontend
- **Framework**: React 18 + Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: Zustand
- **Routing**: React Router v6
- **Real-time**: WebSockets para streaming
- **Testing**: Vitest + React Testing Library

### 6.3 Integraciones
- **Obsidian**: Via GitHub API (el vault se sincroniza con GitHub)
- **Calendars**: Google Calendar API, Microsoft Graph API
- **Email**: Gmail API, Microsoft Graph API
- **WhatsApp**: WhatsApp Business API o Twilio
- **MCPs**: Cliente genérico MCP (reutilizar de AION)

### 6.4 Infraestructura
- **Hosting**: VPS en Hostinger
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Estructurado con structlog
- **Automation**: N8N (ya desplegado)

### 6.5 Testing
- **Unit Tests**: pytest
- **Integration Tests**: pytest + testcontainers
- **E2E Tests**: Playwright
- **Coverage**: >80% para core features

---

## 7. Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                  │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Web App       │   WhatsApp Bot  │   (Future: Voice)           │
│   (Next.js)     │   (Twilio)      │                             │
└────────┬────────┴────────┬────────┴─────────────────────────────┘
         │                 │
         ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY                                 │
│                      (FastAPI)                                   │
├─────────────────────────────────────────────────────────────────┤
│  • Authentication                                                │
│  • Rate Limiting                                                 │
│  • Request Routing                                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CORE SERVICES                                 │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│ Conversation │   English    │   Obsidian   │   Memory           │
│   Agent      │   Tutor      │   Manager    │   Service          │
├──────────────┴──────────────┴──────────────┴────────────────────┤
│  • LLM Orchestration                                             │
│  • Tool Calling                                                  │
│  • Context Management                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE                                │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│   Qdrant     │    Neo4j     │    Redis     │   GitHub API       │
│ (Vectors)    │  (Graph)     │  (Cache)     │  (Obsidian)        │
└──────────────┴──────────────┴──────────────┴────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  OpenRouter  │   Google     │  Microsoft   │   WhatsApp         │
│    (LLM)     │   APIs       │  Graph API   │   (Twilio)         │
└──────────────┴──────────────┴──────────────┴────────────────────┘
```

---

## 8. Modelo de Datos

### 8.1 Entidades Principales

```python
# User (para multi-tenant futuro)
class User:
    id: UUID
    email: str
    name: str
    preferences: dict
    created_at: datetime

# Conversation
class Conversation:
    id: UUID
    user_id: UUID
    started_at: datetime
    messages: list[Message]

# Message
class Message:
    id: UUID
    conversation_id: UUID
    role: "user" | "assistant"
    content: str
    english_corrections: list[Correction] | None
    tools_used: list[ToolCall] | None
    created_at: datetime

# Correction (English tracking)
class Correction:
    id: UUID
    user_id: UUID
    original: str
    corrected: str
    explanation: str
    category: "grammar" | "naturalness" | "vocabulary"
    created_at: datetime

# ObsidianNote
class ObsidianNote:
    path: str
    title: str
    content: str
    tags: list[str]
    created_at: datetime
    modified_at: datetime
```

### 8.2 Relaciones (Neo4j)

```
(User)-[:HAS_CONVERSATION]->(Conversation)
(Conversation)-[:CONTAINS]->(Message)
(User)-[:MADE_ERROR]->(Correction)
(User)-[:KNOWS]->(Person)
(Person)-[:WORKS_AT]->(Company)
(Note)-[:MENTIONS]->(Person)
(Note)-[:RELATED_TO]->(Note)
```

---

## 9. APIs y Endpoints

### 9.1 Chat API

```
POST /api/chat
{
  "message": "I need to create a note about my meeting with John",
  "conversation_id": "uuid" // optional, creates new if not provided
}

Response:
{
  "response": "Sure! Tell me about the meeting...",
  "conversation_id": "uuid",
  "english_corrections": [...],
  "actions_taken": [...]
}
```

### 9.2 Obsidian API

```
GET  /api/obsidian/search?q=meeting+notes
POST /api/obsidian/notes
GET  /api/obsidian/notes/{path}
PUT  /api/obsidian/notes/{path}
```

### 9.3 English Progress API

```
GET /api/english/stats
GET /api/english/corrections?from=2024-01-01
GET /api/english/common-errors
```

---

## 10. Plan de Desarrollo

### Phase 1: Foundation (Semanas 1-3)
- [ ] Setup del proyecto (repo, CI/CD, Docker)
- [ ] Backend básico con FastAPI
- [ ] Integración con OpenRouter
- [ ] Chat simple sin tools
- [ ] Tests básicos

### Phase 2: Core Features (Semanas 4-6)
- [ ] Integración con GitHub/Obsidian
- [ ] Crear Daily Notes desde chat
- [ ] Sistema de corrección de inglés
- [ ] Memoria de conversaciones (Qdrant)
- [ ] Frontend básico (Next.js)

### Phase 3: Productivity (Semanas 7-9)
- [ ] Crear notas de personas
- [ ] Gestión de tareas
- [ ] Búsqueda RAG en vault
- [ ] Recordatorios proactivos

### Phase 4: Integrations (Semanas 10-12)
- [ ] Google Calendar
- [ ] Gmail
- [ ] WhatsApp bot

### Phase 5: Polish (Semanas 13-14)
- [ ] Dashboard de estadísticas
- [ ] Mejoras de UX
- [ ] Documentación
- [ ] Testing E2E

---

## 11. Métricas de Éxito

### 11.1 Engagement
- Daily Active Usage (objetivo: 5+ días/semana)
- Messages per day (objetivo: 10+)
- Retention: sigue usándolo después de 1 mes

### 11.2 Productividad
- Notas creadas via Dave vs manualmente
- Tiempo ahorrado en organización

### 11.3 Inglés
- Reducción de errores repetidos
- Nuevas palabras/frases incorporadas
- Streak de práctica

---

## 12. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Costos de API altos | Media | Alto | Usar modelos más baratos para tareas simples, caching |
| Complejidad de integraciones | Alta | Medio | Empezar con menos integraciones, usar MCPs genéricos |
| Pérdida de interés | Media | Alto | MVP rápido, iterar basado en uso real |
| Sync conflicts con Obsidian | Media | Medio | Esperar a que GitHub sync complete antes de modificar |

---

## 13. Open Questions

1. ¿Dave debería poder modificar notas existentes o solo crear nuevas?
	- debería poder modificar notas existentes (siempre informando sobre la modificación)
2. ¿Cómo manejar cuando el usuario escribe en español? ¿Traducir o responder en español?
	- Inicialmente prefiero que siempre responda en inlgés, pero me gustaría que esto se pueda cambiar fácilmente en el futuro
3. ¿Nivel de detalle en las correcciones de inglés? ¿Configurable?
	- Prefiero que sea configurable: activo / inactivo y cuando se activa, que tenga niveles
4. ¿Qué tan agresivo con los recordatorios proactivos?
	- Que sea algo intermedio, no muy intrusivo pero que ayude a mantener la constancia

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2024-11-22 | Initial draft |
