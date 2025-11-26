---
created: 2025-11-26
tags:
  - project
  - markdown-editor
  - obsidian
  - notion
  - feature-planning
status: draft
---

# Editor de Markdown - Plan de Desarrollo

## 1. Resumen Ejecutivo

### Objetivo
Crear un editor de Markdown integrado en Dave que permita editar archivos de Obsidian directamente desde la aplicación web, replicando las funcionalidades esenciales de Obsidian y Notion.

### Contexto Actual
- Dave actualmente se conecta a Obsidian vía GitHub API (lectura)
- Los usuarios pueden visualizar archivos markdown pero no editarlos
- La sincronización es unidireccional (GitHub → Dave)

### Visión del Editor
Un editor WYSIWYG (What You See Is What You Get) potenciado por IA que permita:
- Editar archivos markdown con vista previa en tiempo real
- Guardar cambios directamente en el repositorio de GitHub
- Soporte para sintaxis avanzada de Obsidian (wikilinks, tags, frontmatter)
- Experiencia de usuario similar a Notion (editor fluido y moderno)
- **Asistencia de IA integrada para escribir mejor y más rápido**
  - Asistente de escritura (Cmd+K) para mejorar texto
  - Corrección de inglés en tiempo real
  - Generación de contenido con comandos `/ai`
  - Chat contextual con Dave
  - Sugerencias inteligentes de links y metadata

---

## 2. Historias de Usuario

### Resumen de Épics

| Epic | Historias | Descripción | Prioridad |
|------|-----------|-------------|-----------|
| **Epic 1** | US-001 a US-003 | Visualización y Edición Básica | Alta |
| **Epic 2** | US-004 a US-006 | Funcionalidades de Formato Básico | Media |
| **Epic 3** | US-007 a US-009 | Funcionalidades Avanzadas de Obsidian | Alta |
| **Epic 4** | US-010 a US-012 | Funcionalidades Estilo Notion | Baja |
| **Epic 5** | US-013 a US-015 | Experiencia de Usuario | Alta |
| **Epic 6** | US-016 a US-017 | Creación de Contenido | Media |
| **Epic 7** | US-018 a US-019 | Colaboración y Sincronización | Alta |
| **Epic 8** | US-020 a US-029 | **Asistencia IA en el Editor** | **Alta** |

### Epic 8: Resumen de Funcionalidades de IA

El Epic 8 transforma el editor en un asistente de escritura inteligente con 10 historias de usuario que cubren:

**Funcionalidades Core (Alta prioridad):**
- **US-020**: Asistente de escritura IA (Cmd+K) - Mejora y modifica texto con instrucciones naturales
- **US-021**: Corrección de inglés en tiempo real - Marca y corrige errores mientras escribes
- **US-022**: Generación de contenido con IA - Comandos `/ai` para generar, resumir, expandir, etc.

**Funcionalidades Avanzadas (Media prioridad):**
- **US-025**: Generación automática de títulos, resúmenes y tags
- **US-026**: Chat contextual con Dave dentro del editor
- **US-027**: Ajuste de tono y estilo (formal, casual, técnico, etc.)
- **US-028**: Sugerencias inteligentes de wikilinks basadas en contenido

**Funcionalidades Opcionales (Baja prioridad):**
- **US-023**: Autocompletado inteligente estilo GitHub Copilot
- **US-024**: Análisis y sugerencias de estructura del documento
- **US-029**: Detección de contenido duplicado y consolidación

Estas funcionalidades aprovechan la infraestructura de LLM existente en Dave y se integran perfectamente con el sistema de aprendizaje de inglés.

---

### Epic 1: Visualización y Edición Básica

#### US-001: Abrir archivo en modo edición
**Como** usuario de Dave
**Quiero** poder abrir un archivo markdown en modo edición
**Para** modificar el contenido de mis notas de Obsidian

**Criterios de Aceptación:**
- [ ] Hay un botón "Edit" en el FileViewer
- [ ] Al hacer clic, el contenido se muestra en un editor
- [ ] El editor muestra el markdown raw por defecto
- [ ] Puedo alternar entre vista raw y vista preview

**Prioridad:** Alta
**Estimación:** 3 puntos

---

#### US-002: Guardar cambios en GitHub
**Como** usuario de Dave
**Quiero** guardar los cambios que hago en un archivo
**Para** que se sincronicen con mi repositorio de Obsidian

**Criterios de Aceptación:**
- [ ] Hay un botón "Save" visible cuando hay cambios sin guardar
- [ ] Al guardar, se hace commit en GitHub con el SHA correcto
- [ ] Se muestra un mensaje de confirmación
- [ ] Se muestra un mensaje de error si falla
- [ ] Los cambios se reflejan inmediatamente en la vista

**Prioridad:** Alta
**Estimación:** 5 puntos

---

#### US-003: Detectar cambios sin guardar
**Como** usuario de Dave
**Quiero** saber si tengo cambios sin guardar
**Para** no perder mi trabajo accidentalmente

**Criterios de Aceptación:**
- [ ] Indicador visual cuando hay cambios sin guardar
- [ ] Advertencia al cerrar el editor con cambios sin guardar
- [ ] Advertencia al navegar a otro archivo
- [ ] Opción de descartar cambios

**Prioridad:** Alta
**Estimación:** 3 puntos

---

### Epic 2: Funcionalidades de Formato Básico

#### US-004: Aplicar formato con atajos de teclado
**Como** usuario de Dave
**Quiero** usar atajos de teclado para formatear texto
**Para** escribir más rápido sin usar el mouse

**Criterios de Aceptación:**
- [ ] Cmd/Ctrl + B para negrita
- [ ] Cmd/Ctrl + I para cursiva
- [ ] Cmd/Ctrl + K para links
- [ ] Cmd/Ctrl + E para código inline
- [ ] Cmd/Ctrl + Shift + E para bloque de código

**Prioridad:** Media
**Estimación:** 5 puntos

---

#### US-005: Barra de herramientas de formato
**Como** usuario de Dave
**Quiero** una barra de herramientas visual
**Para** aplicar formato sin recordar atajos de teclado

**Criterios de Aceptación:**
- [ ] Barra flotante aparece al seleccionar texto
- [ ] Botones: Bold, Italic, Code, Link, Highlight
- [ ] Los botones muestran el estado actual (activo/inactivo)
- [ ] La barra se posiciona cerca del texto seleccionado

**Prioridad:** Media
**Estimación:** 8 puntos

---

#### US-006: Autocompletado de sintaxis markdown
**Como** usuario de Dave
**Quiero** que el editor autocomplete sintaxis markdown
**Para** escribir más rápido

**Criterios de Aceptación:**
- [ ] Escribir `**` cierra automáticamente con `**`
- [ ] Escribir `[[` cierra con `]]` (wikilinks)
- [ ] Escribir ` ``` ` crea bloque de código
- [ ] Las listas se continúan automáticamente
- [ ] Los checkboxes se crean con `- [ ]`

**Prioridad:** Media
**Estimación:** 5 puntos

---

### Epic 3: Funcionalidades Avanzadas de Obsidian

#### US-007: Soporte para Wikilinks
**Como** usuario de Dave
**Quiero** crear y seguir wikilinks
**Para** navegar entre mis notas

**Criterios de Aceptación:**
- [ ] `[[nombre de nota]]` se renderiza como link clickeable
- [ ] Al hacer clic, se abre la nota referenciada
- [ ] Autocompletado al escribir `[[` con lista de notas
- [ ] Soporte para aliases: `[[nota|alias]]`
- [ ] Indicador visual para links rotos

**Prioridad:** Alta
**Estimación:** 8 puntos

---

#### US-008: Soporte para Tags
**Como** usuario de Dave
**Quiero** usar tags en mis notas
**Para** organizar y categorizar mi contenido

**Criterios de Aceptación:**
- [ ] `#tag` se renderiza con estilo especial
- [ ] Autocompletado de tags existentes
- [ ] Los tags son clickeables
- [ ] Al hacer clic, se muestran todas las notas con ese tag
- [ ] Soporte para nested tags: `#tag/subtag`

**Prioridad:** Media
**Estimación:** 5 puntos

---

#### US-009: Editor de Frontmatter
**Como** usuario de Dave
**Quiero** editar el frontmatter de forma visual
**Para** no tener que escribir YAML manualmente

**Criterios de Aceptación:**
- [ ] El frontmatter se muestra en un panel separado
- [ ] Campos comunes tienen inputs dedicados (title, tags, date)
- [ ] Se puede agregar campos personalizados
- [ ] El YAML se genera automáticamente
- [ ] Validación de sintaxis YAML

**Prioridad:** Baja
**Estimación:** 8 puntos

---

### Epic 4: Funcionalidades Estilo Notion

#### US-010: Bloques de contenido arrastrable
**Como** usuario de Dave
**Quiero** reorganizar bloques de contenido arrastrando
**Para** reestructurar mis notas fácilmente

**Criterios de Aceptación:**
- [ ] Cada párrafo/bloque tiene un handle de arrastre
- [ ] Puedo arrastrar bloques arriba/abajo
- [ ] Indicador visual durante el arrastre
- [ ] El markdown se actualiza correctamente
- [ ] Funciona con listas, headings, párrafos

**Prioridad:** Baja
**Estimación:** 13 puntos

---

#### US-011: Menú de comandos con /
**Como** usuario de Dave
**Quiero** escribir `/` para ver un menú de comandos
**Para** insertar diferentes tipos de bloques rápidamente

**Criterios de Aceptación:**
- [ ] Escribir `/` muestra menú de comandos
- [ ] Opciones: heading, list, checkbox, code, table, divider
- [ ] Búsqueda filtrada al escribir
- [ ] Navegación con teclado (arriba/abajo, enter)
- [ ] Se inserta el bloque correspondiente

**Prioridad:** Media
**Estimación:** 8 puntos

---

#### US-012: Menciones con @
**Como** usuario de Dave
**Quiero** usar `@` para mencionar otras notas o personas
**Para** crear referencias rápidas

**Criterios de Aceptación:**
- [ ] Escribir `@` muestra menú de notas
- [ ] Búsqueda filtrada por nombre de nota
- [ ] Se convierte en wikilink al seleccionar
- [ ] Soporte para menciones a personas/recursos

**Prioridad:** Baja
**Estimación:** 5 puntos

---

### Epic 5: Experiencia de Usuario

#### US-013: Vista previa en tiempo real
**Como** usuario de Dave
**Quiero** ver el markdown renderizado mientras escribo
**Para** tener feedback inmediato de cómo se ve

**Criterios de Aceptación:**
- [ ] Vista dividida (editor | preview)
- [ ] La preview se actualiza mientras escribo (debounced)
- [ ] Scroll sincronizado entre editor y preview
- [ ] Toggle para mostrar/ocultar preview
- [ ] Preview usa los mismos estilos que el FileViewer

**Prioridad:** Alta
**Estimación:** 8 puntos

---

#### US-014: Modo focus
**Como** usuario de Dave
**Quiero** un modo de escritura sin distracciones
**Para** concentrarme en el contenido

**Criterios de Aceptación:**
- [ ] Botón para activar modo focus
- [ ] Oculta sidebars y toolbars
- [ ] Centra el contenido
- [ ] Ancho máximo confortable para lectura
- [ ] Se sale con Esc

**Prioridad:** Baja
**Estimación:** 3 puntos

---

#### US-015: Historial de versiones
**Como** usuario de Dave
**Quiero** ver versiones anteriores de un archivo
**Para** poder recuperar contenido perdido

**Criterios de Aceptación:**
- [ ] Botón "History" en el editor
- [ ] Lista de commits de GitHub para ese archivo
- [ ] Puedo ver el contenido de cada versión
- [ ] Puedo restaurar una versión anterior
- [ ] Muestra autor y fecha de cada versión

**Prioridad:** Baja
**Estimación:** 13 puntos

---

### Epic 6: Creación de Contenido

#### US-016: Crear nueva nota desde el editor
**Como** usuario de Dave
**Quiero** crear una nueva nota desde cualquier lugar
**Para** capturar ideas rápidamente

**Criterios de Aceptación:**
- [ ] Botón "New Note" visible en toda la app
- [ ] Modal para elegir template y ubicación
- [ ] Se crea el archivo en GitHub
- [ ] Se abre automáticamente en el editor
- [ ] Se puede crear desde wikilink roto

**Prioridad:** Media
**Estimación:** 8 puntos

---

#### US-017: Templates de notas
**Como** usuario de Dave
**Quiero** crear notas desde templates
**Para** mantener consistencia en mis notas

**Criterios de Aceptación:**
- [ ] Templates predefinidos (daily note, meeting, person, project)
- [ ] Los templates incluyen frontmatter
- [ ] Se pueden crear templates personalizados
- [ ] Variables en templates: {{date}}, {{title}}
- [ ] Templates se guardan en carpeta especial del vault

**Prioridad:** Baja
**Estimación:** 13 puntos

---

### Epic 7: Colaboración y Sincronización

#### US-018: Detección de conflictos
**Como** usuario de Dave
**Quiero** saber si alguien más editó el archivo
**Para** no sobrescribir cambios de otros

**Criterios de Aceptación:**
- [ ] Al guardar, verifica que el SHA no haya cambiado
- [ ] Si cambió, muestra advertencia de conflicto
- [ ] Muestra diff entre mi versión y la actual
- [ ] Opciones: sobrescribir, descartar, fusionar manualmente
- [ ] Previene pérdida de datos

**Prioridad:** Alta
**Estimación:** 13 puntos

---

#### US-019: Auto-guardado
**Como** usuario de Dave
**Quiero** que mis cambios se guarden automáticamente
**Para** no perder trabajo si olvido guardar

**Criterios de Aceptación:**
- [ ] Auto-guardado cada 30 segundos de inactividad
- [ ] Indicador visual de "guardando..."
- [ ] Se puede desactivar en configuración
- [ ] Solo guarda si hay cambios reales
- [ ] Mensajes de commit descriptivos

**Prioridad:** Media
**Estimación:** 5 puntos

---

### Epic 8: Asistencia IA en el Editor

#### US-020: Asistente de escritura IA
**Como** usuario de Dave
**Quiero** pedirle a la IA que me ayude a escribir o mejorar texto
**Para** crear contenido de mejor calidad más rápidamente

**Criterios de Aceptación:**
- [ ] Selecciono texto y presiono Cmd+K o botón "Ask AI"
- [ ] Aparece input para escribir instrucción (ej: "mejora esto", "hazlo más formal")
- [ ] La IA genera una sugerencia basada en el texto seleccionado
- [ ] Puedo aceptar, rechazar o editar la sugerencia
- [ ] La sugerencia reemplaza el texto original al aceptar
- [ ] Historial de sugerencias por si quiero volver atrás

**Ejemplos de uso:**
- "Resume este párrafo"
- "Expande esta idea"
- "Hazlo más profesional"
- "Escribe una introducción para esta sección"
- "Genera ideas de contenido sobre [tema]"

**Prioridad:** Alta
**Estimación:** 13 puntos

---

#### US-021: Corrección de inglés en tiempo real
**Como** usuario de Dave
**Quiero** que la IA corrija automáticamente mis errores de inglés
**Para** escribir en inglés correctamente sin interrupciones

**Criterios de Aceptación:**
- [ ] Toggle "English Corrections" en el toolbar
- [ ] Al activar, analiza el texto mientras escribo (debounced)
- [ ] Marca errores con subrayado de color (gramática, ortografía, naturalidad)
- [ ] Al hacer hover, muestra explicación y sugerencia
- [ ] Al hacer clic, aplica la corrección automáticamente
- [ ] Panel lateral con lista de todas las correcciones sugeridas
- [ ] Puedo ignorar sugerencias individuales
- [ ] Se integra con el sistema de aprendizaje de inglés existente

**Tipos de correcciones:**
- Gramática (verb tenses, articles, prepositions)
- Ortografía (typos, capitalization)
- Naturalidad (phrasing más nativo)
- Vocabulario (better word choices)

**Prioridad:** Alta
**Estimación:** 13 puntos

---

#### US-022: Generación de contenido con IA
**Como** usuario de Dave
**Quiero** usar comandos de IA para generar contenido
**Para** acelerar la creación de notas

**Criterios de Aceptación:**
- [ ] Escribir `/ai` muestra menú de comandos de IA
- [ ] Opciones disponibles:
  - `/ai generate` - Generar contenido sobre un tema
  - `/ai summarize` - Resumir contenido existente
  - `/ai expand` - Expandir bullet points
  - `/ai brainstorm` - Generar ideas
  - `/ai translate` - Traducir texto
  - `/ai tone` - Cambiar tono (formal/casual/profesional)
- [ ] Cada comando muestra input para parámetros
- [ ] Genera contenido e inserta en el cursor
- [ ] Se puede regenerar si no satisface
- [ ] Indicador visual mientras genera

**Prioridad:** Media
**Estimación:** 8 puntos

---

#### US-023: Autocompletado inteligente con IA
**Como** usuario de Dave
**Quiero** sugerencias de autocompletado basadas en contexto
**Para** escribir más rápido con sugerencias relevantes

**Criterios de Aceptación:**
- [ ] Mientras escribo, la IA sugiere completaciones (estilo GitHub Copilot)
- [ ] Las sugerencias aparecen en gris después del cursor
- [ ] Presiono Tab para aceptar la sugerencia
- [ ] Presiono Esc para rechazar
- [ ] Las sugerencias consideran:
  - Contexto del documento (título, sección actual)
  - Historial de escritura del usuario
  - Notas relacionadas en el vault
- [ ] Se puede desactivar en configuración
- [ ] No interrumpe el flujo de escritura

**Prioridad:** Baja
**Estimación:** 13 puntos

---

#### US-024: Análisis y sugerencias de estructura
**Como** usuario de Dave
**Quiero** que la IA analice la estructura de mi documento
**Para** mejorar la organización y claridad

**Criterios de Aceptación:**
- [ ] Botón "Analyze Document" en el toolbar
- [ ] La IA analiza:
  - Estructura de headings (jerarquía, balance)
  - Longitud de secciones
  - Coherencia y flujo
  - Gaps en el contenido
- [ ] Muestra sugerencias específicas:
  - "Considera dividir esta sección en subsecciones"
  - "Esta sección está muy corta, considera expandir"
  - "Falta transición entre estas secciones"
  - "Podrías agregar una conclusión"
- [ ] Panel lateral con todas las sugerencias
- [ ] Al hacer clic, navega a la sección relevante
- [ ] Puedo marcar sugerencias como "completadas"

**Prioridad:** Baja
**Estimación:** 8 puntos

---

#### US-025: Generación de títulos y resúmenes
**Como** usuario de Dave
**Quiero** que la IA genere títulos y resúmenes automáticamente
**Para** ahorrar tiempo en metadata

**Criterios de Aceptación:**
- [ ] Botón "Generate Metadata" en el toolbar
- [ ] La IA analiza el contenido y sugiere:
  - Título descriptivo (si está vacío o es placeholder)
  - Resumen de 1-2 líneas
  - Tags relevantes basados en contenido
  - Categoría/tipo de nota
- [ ] Muestra preview de las sugerencias
- [ ] Puedo aceptar todas, aceptar individualmente, o editar
- [ ] Se actualiza el frontmatter automáticamente
- [ ] También funciona para notas existentes

**Prioridad:** Media
**Estimación:** 5 puntos

---

#### US-026: Chat contextual en el editor
**Como** usuario de Dave
**Quiero** abrir un chat con Dave sin salir del editor
**Para** obtener ayuda sobre el contenido actual

**Criterios de Aceptación:**
- [ ] Botón "Chat with Dave" abre panel lateral
- [ ] Dave tiene contexto del documento actual
- [ ] Puedo hacer preguntas sobre:
  - El contenido que estoy editando
  - Ideas para continuar escribiendo
  - Clarificación de conceptos
  - Referencias de otras notas
- [ ] Las respuestas pueden insertarse en el documento
- [ ] El chat se mantiene mientras edito
- [ ] Historial del chat persiste por sesión

**Ejemplos de preguntas:**
- "¿Qué más debería incluir en esta sección?"
- "¿Tengo otras notas sobre este tema?"
- "Dame ejemplos de [concepto]"
- "¿Cómo puedo mejorar esta explicación?"

**Prioridad:** Media
**Estimación:** 8 puntos

---

#### US-027: Mejora de tono y estilo
**Como** usuario de Dave
**Quiero** ajustar el tono de mi escritura
**Para** adaptarla a diferentes contextos

**Criterios de Aceptación:**
- [ ] Selecciono texto y elijo "Adjust Tone"
- [ ] Opciones de tono disponibles:
  - Más formal/profesional
  - Más casual/conversacional
  - Más conciso
  - Más detallado
  - Más amigable
  - Más técnico
  - Más simple (ELI5)
- [ ] Preview de cómo quedaría el texto
- [ ] Comparación lado a lado (original vs ajustado)
- [ ] Puedo aplicar o seguir editando
- [ ] Mantiene el significado original

**Prioridad:** Media
**Estimación:** 5 puntos

---

#### US-028: Referencias inteligentes
**Como** usuario de Dave
**Quiero** que la IA sugiera referencias a otras notas
**Para** crear conexiones relevantes en mi vault

**Criterios de Aceptación:**
- [ ] Panel "Suggested Links" en el sidebar
- [ ] Mientras escribo, la IA identifica:
  - Conceptos mencionados que tienen notas dedicadas
  - Temas relacionados con notas existentes
  - Personas/proyectos que tienen su propia nota
- [ ] Lista de sugerencias con snippet del contenido
- [ ] Click para insertar wikilink en el cursor
- [ ] Se puede ignorar sugerencias no relevantes
- [ ] Aprende de mis patrones de linking

**Prioridad:** Baja
**Estimación:** 13 puntos

---

#### US-029: Detección de duplicados y consolidación
**Como** usuario de Dave
**Quiero** que la IA detecte contenido duplicado
**Para** mantener mi vault organizado y sin redundancia

**Criterios de Aceptación:**
- [ ] Al guardar, la IA verifica similaridad con otras notas
- [ ] Si detecta contenido muy similar (>80%), muestra advertencia
- [ ] Muestra las notas similares con comparación de contenido
- [ ] Opciones:
  - Continuar guardando (está bien la duplicación)
  - Ver notas similares para decidir
  - Sugerir consolidación (merge)
- [ ] Al consolidar, la IA ayuda a combinar contenido
- [ ] Mantiene referencias (wikilinks) actualizadas

**Prioridad:** Baja
**Estimación:** 13 puntos

---

## 3. Arquitectura Técnica

### 3.1 Stack Tecnológico

#### Editor Core
- **Librería base**: [Lexical](https://lexical.dev/) (Meta's text editor framework)
  - Alternativa: [ProseMirror](https://prosemirror.net/) o [TipTap](https://tiptap.dev/)
  - Razón: Lexical es moderno, performante y fácil de extender

#### Parsing y Rendering
- **Markdown Parser**: [unified](https://unifiedjs.com/) + [remark](https://github.com/remarkjs/remark)
  - Para parsear markdown a AST
  - Plugins para wikilinks, frontmatter, etc.
- **Syntax Highlighting**: [Prism.js](https://prismjs.com/) o [Shiki](https://shiki.matsu.io/)

#### State Management
- **Editor State**: Lexical's internal state
- **Document State**: Zustand store
- **Sync State**: React Query para mutations de GitHub API

#### Componentes UI
- **Iconos**: Lucide React (ya en uso)
- **Tooltips**: Radix UI
- **Drag & Drop**: [@dnd-kit](https://dndkit.com/)

---

### 3.2 Arquitectura de Componentes

```typescript
// Estructura de componentes

frontend/src/components/editor/
├── MarkdownEditor.tsx          // Componente principal
├── EditorToolbar.tsx            // Barra de herramientas superior
├── EditorSidebar.tsx            // Panel lateral (outline, metadata)
├── FloatingToolbar.tsx          // Toolbar que aparece al seleccionar
├── CommandMenu.tsx              // Menú de comandos (/)
├── EditorContent.tsx            // Área de contenido editable
├── PreviewPane.tsx              // Vista previa en tiempo real
├── FrontmatterEditor.tsx        // Editor de frontmatter
├── FileMetadata.tsx             // Metadata del archivo (size, modified, etc)
├── SaveIndicator.tsx            // Indicador de guardado
├── ConflictResolver.tsx         // UI para resolver conflictos
│
├── ai/                          // Componentes de IA
│   ├── AIAssistantPanel.tsx     // Panel de asistente IA (Cmd+K)
│   ├── AICommandMenu.tsx        // Menú de comandos /ai
│   ├── EnglishCorrections.tsx   // Panel de correcciones de inglés
│   ├── AIAutoComplete.tsx       // Sugerencias de autocompletado
│   ├── StructureAnalysis.tsx    // Análisis de estructura
│   ├── SuggestedLinks.tsx       // Sugerencias de wikilinks
│   ├── ToneAdjuster.tsx         // UI para ajustar tono
│   ├── ChatSidebar.tsx          // Chat contextual con Dave
│   └── AIGenerationModal.tsx    // Modal para generación de contenido
│
├── plugins/                     // Plugins de Lexical
│   ├── WikiLinkPlugin.tsx       // Soporte para [[wikilinks]]
│   ├── TagPlugin.tsx            // Soporte para #tags
│   ├── SlashCommandPlugin.tsx   // Menú de comandos (/)
│   ├── MentionPlugin.tsx        // Menciones con @
│   ├── MarkdownShortcutsPlugin.tsx  // Atajos markdown (**, ##, etc)
│   ├── AutoSavePlugin.tsx       // Auto-guardado
│   ├── ToolbarPlugin.tsx        // Control de toolbar
│   ├── AIAssistantPlugin.tsx    // Integración de asistente IA
│   ├── EnglishCorrectionPlugin.tsx  // Correcciones en tiempo real
│   └── AIAutoCompletePlugin.tsx // Autocompletado inteligente
│
├── nodes/                       // Custom Lexical nodes
│   ├── WikiLinkNode.ts          // Nodo para wikilinks
│   ├── TagNode.ts               // Nodo para tags
│   ├── CalloutNode.ts           // Nodo para callouts
│   ├── EmbedNode.ts             // Nodo para embeds
│   └── CorrectionMarkNode.ts    // Nodo para marcar correcciones
│
└── utils/
    ├── markdown.ts              // Helpers para markdown
    ├── wikilinks.ts             // Parsing de wikilinks
    ├── frontmatter.ts           // Parsing de frontmatter
    ├── sync.ts                  // Lógica de sincronización
    └── ai.ts                    // Utilidades para IA
```

---

### 3.3 Flujo de Datos

```
┌─────────────────────────────────────────────────────┐
│                  Editor State                       │
│  (Lexical EditorState - AST del documento)          │
└────────────┬────────────────────────────────────────┘
             │
             ├─── onChange ──────────────────────────┐
             │                                       │
             ▼                                       ▼
┌─────────────────────────┐            ┌─────────────────────────┐
│   Markdown Serializer   │            │    Preview Renderer     │
│  (AST → Markdown text)  │            │  (AST → React elements) │
└────────────┬────────────┘            └─────────────────────────┘
             │
             ▼
┌─────────────────────────┐
│  Unsaved Changes State  │
└────────────┬────────────┘
             │
             ├─── Manual Save or Auto-save trigger ──────┐
             │                                            │
             ▼                                            ▼
┌─────────────────────────┐                  ┌─────────────────────┐
│   GitHub API Client     │ ───────────────▶ │   GitHub Repository │
│  (PUT /vault/file)      │                  │   (Obsidian Vault)  │
└─────────────────────────┘                  └─────────────────────┘
```

---

### 3.4 Backend - Extensiones API

Necesitamos extender las rutas de vault para soportar edición:

```python
# backend/src/api/routes/vault.py

@router.put("/vault/file/content")
async def update_file_content(
    path: str,
    content: str,
    sha: str,
    message: str | None = None
) -> dict:
    """Update file content with conflict detection."""

    client = get_github_vault_client()

    # Verify SHA hasn't changed (conflict detection)
    current_file = await client.get_file(path)
    if current_file["sha"] != sha:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "conflict",
                "current_sha": current_file["sha"],
                "current_content": current_file["content"]
            }
        )

    # Update file
    result = await client.update_file(path, content, sha, message)
    return {"status": "updated", "sha": result["content"]["sha"]}


@router.post("/vault/file/create")
async def create_new_file(
    path: str,
    content: str,
    message: str | None = None
) -> dict:
    """Create a new file in the vault."""

    client = get_github_vault_client()

    # Check if file exists
    existing = await client.get_file(path)
    if existing:
        raise HTTPException(status_code=409, detail="File already exists")

    result = await client.create_file(path, content, message)
    return {
        "status": "created",
        "path": path,
        "sha": result["content"]["sha"]
    }


@router.get("/vault/file/history")
async def get_file_history(path: str, limit: int = 20) -> list[dict]:
    """Get commit history for a file."""

    client = get_github_vault_client()

    # Call GitHub commits API
    commits = await client.get_file_commits(path, limit)

    return [
        {
            "sha": commit["sha"],
            "message": commit["commit"]["message"],
            "author": commit["commit"]["author"]["name"],
            "date": commit["commit"]["author"]["date"],
        }
        for commit in commits
    ]


@router.get("/vault/file/version")
async def get_file_version(path: str, sha: str) -> dict:
    """Get a specific version of a file."""

    client = get_github_vault_client()
    content = await client.get_file_at_commit(path, sha)

    return {
        "path": path,
        "sha": sha,
        "content": content
    }
```

#### APIs de IA para el Editor

```python
# backend/src/api/routes/editor_ai.py

router = APIRouter(prefix="/api/v1/editor/ai", tags=["editor-ai"])


class AIAssistRequest(BaseModel):
    text: str
    instruction: str
    context: dict | None = None  # Documento completo, título, etc.


class EnglishCorrectionRequest(BaseModel):
    text: str
    language_level: str = "intermediate"  # beginner, intermediate, advanced


class ContentGenerationRequest(BaseModel):
    command: str  # generate, summarize, expand, brainstorm, etc.
    input_text: str | None = None
    parameters: dict  # topic, style, length, etc.
    context: dict | None = None


class StructureAnalysisRequest(BaseModel):
    content: str
    frontmatter: dict


class SimilarNotesRequest(BaseModel):
    content: str
    min_similarity: float = 0.7


@router.post("/assist")
async def ai_assist(request: AIAssistRequest) -> dict:
    """
    Asistente general de IA para mejorar/modificar texto.
    Usa LLM para aplicar la instrucción al texto dado.
    """
    use_case = AIAssistUseCase()
    result = await use_case.execute(
        text=request.text,
        instruction=request.instruction,
        context=request.context
    )

    return {
        "original": request.text,
        "suggestion": result.suggestion,
        "explanation": result.explanation
    }


@router.post("/correct-english")
async def correct_english(request: EnglishCorrectionRequest) -> dict:
    """
    Analiza texto en inglés y devuelve correcciones.
    Integrado con el sistema de aprendizaje de inglés.
    """
    analyzer = EnglishAnalyzer()
    corrections = await analyzer.analyze_with_corrections(
        text=request.text,
        level=request.language_level
    )

    return {
        "corrections": [
            {
                "original": c.original,
                "suggestion": c.suggestion,
                "category": c.category,
                "explanation": c.explanation,
                "start": c.start_pos,
                "end": c.end_pos
            }
            for c in corrections
        ]
    }


@router.post("/generate")
async def generate_content(request: ContentGenerationRequest) -> dict:
    """
    Genera contenido basado en comandos de IA.
    Comandos: generate, summarize, expand, brainstorm, translate, tone.
    """
    use_case = ContentGenerationUseCase()
    result = await use_case.execute(
        command=request.command,
        input_text=request.input_text,
        parameters=request.parameters,
        context=request.context
    )

    return {
        "generated_content": result.content,
        "metadata": result.metadata  # word_count, tokens_used, etc.
    }


@router.post("/autocomplete")
async def autocomplete(text: str, cursor_position: int, context: dict) -> dict:
    """
    Genera sugerencias de autocompletado basadas en contexto.
    """
    use_case = AutoCompleteUseCase()
    suggestions = await use_case.execute(
        text=text,
        cursor_pos=cursor_position,
        context=context
    )

    return {
        "suggestions": suggestions  # Lista de posibles completaciones
    }


@router.post("/analyze-structure")
async def analyze_structure(request: StructureAnalysisRequest) -> dict:
    """
    Analiza la estructura del documento y sugiere mejoras.
    """
    use_case = StructureAnalysisUseCase()
    analysis = await use_case.execute(
        content=request.content,
        frontmatter=request.frontmatter
    )

    return {
        "headings": analysis.heading_structure,
        "suggestions": [
            {
                "type": s.type,  # structure, balance, flow, gap
                "message": s.message,
                "section": s.section_name,
                "severity": s.severity  # info, warning, suggestion
            }
            for s in analysis.suggestions
        ],
        "metrics": {
            "word_count": analysis.word_count,
            "reading_time": analysis.reading_time_minutes,
            "section_balance": analysis.section_balance_score
        }
    }


@router.post("/generate-metadata")
async def generate_metadata(content: str) -> dict:
    """
    Genera título, resumen y tags basados en el contenido.
    """
    use_case = MetadataGenerationUseCase()
    metadata = await use_case.execute(content)

    return {
        "title": metadata.suggested_title,
        "summary": metadata.suggested_summary,
        "tags": metadata.suggested_tags,
        "category": metadata.suggested_category
    }


@router.post("/suggest-links")
async def suggest_links(content: str, current_path: str) -> dict:
    """
    Sugiere wikilinks relevantes basados en el contenido.
    Usa RAG para encontrar notas similares.
    """
    use_case = SuggestLinksUseCase()
    suggestions = await use_case.execute(
        content=content,
        exclude_path=current_path
    )

    return {
        "suggestions": [
            {
                "note_path": s.path,
                "note_title": s.title,
                "relevance_score": s.score,
                "snippet": s.snippet,
                "suggested_text": s.anchor_text  # Texto donde insertar link
            }
            for s in suggestions
        ]
    }


@router.post("/find-similar")
async def find_similar_notes(request: SimilarNotesRequest) -> dict:
    """
    Detecta notas similares para evitar duplicación.
    """
    use_case = FindSimilarNotesUseCase()
    similar = await use_case.execute(
        content=request.content,
        min_similarity=request.min_similarity
    )

    return {
        "similar_notes": [
            {
                "path": n.path,
                "title": n.title,
                "similarity_score": n.similarity,
                "overlapping_content": n.overlaps
            }
            for n in similar
        ]
    }


@router.post("/adjust-tone")
async def adjust_tone(text: str, target_tone: str) -> dict:
    """
    Ajusta el tono del texto según el objetivo.
    Tonos: formal, casual, concise, detailed, friendly, technical, simple.
    """
    use_case = ToneAdjusterUseCase()
    result = await use_case.execute(
        text=text,
        tone=target_tone
    )

    return {
        "original": text,
        "adjusted": result.adjusted_text,
        "changes": result.key_changes
    }
```

---

### 3.5 Modelos de Datos

```typescript
// frontend/src/types/editor.ts

export interface EditorDocument {
  path: string
  content: string
  sha: string
  frontmatter: Record<string, any>
  hasUnsavedChanges: boolean
  lastSaved: Date | null
}

export interface EditorState {
  currentDocument: EditorDocument | null
  isEditing: boolean
  isSaving: boolean
  saveError: string | null
  conflictState: ConflictState | null
}

export interface ConflictState {
  localContent: string
  remoteContent: string
  remoteSha: string
}

export interface SaveOptions {
  autoSave: boolean
  commitMessage?: string
  createIfNotExists: boolean
}

export interface WikiLink {
  text: string
  target: string
  alias?: string
  exists: boolean
}

export interface Tag {
  name: string
  count: number // Número de notas con este tag
}
```

---

### 3.6 Store de Zustand para Editor

```typescript
// frontend/src/stores/editorStore.ts

interface EditorStore {
  // State
  document: EditorDocument | null
  isEditing: boolean
  isSaving: boolean
  saveError: string | null
  conflictState: ConflictState | null

  // Actions
  openDocument: (path: string) => Promise<void>
  updateContent: (content: string) => void
  saveDocument: (message?: string) => Promise<void>
  closeDocument: () => void
  discardChanges: () => void
  resolveConflict: (strategy: 'local' | 'remote' | 'manual') => Promise<void>

  // Config
  autoSaveEnabled: boolean
  autoSaveInterval: number // seconds
  setAutoSave: (enabled: boolean) => void
}

export const useEditorStore = create<EditorStore>((set, get) => ({
  document: null,
  isEditing: false,
  isSaving: false,
  saveError: null,
  conflictState: null,
  autoSaveEnabled: true,
  autoSaveInterval: 30,

  openDocument: async (path: string) => {
    const file = await getVaultFile(path)
    const { frontmatter, content } = parseFrontmatter(file.content)

    set({
      document: {
        path,
        content,
        sha: file.sha,
        frontmatter,
        hasUnsavedChanges: false,
        lastSaved: null
      },
      isEditing: true
    })
  },

  updateContent: (content: string) => {
    const doc = get().document
    if (!doc) return

    set({
      document: {
        ...doc,
        content,
        hasUnsavedChanges: true
      }
    })
  },

  saveDocument: async (message?: string) => {
    const doc = get().document
    if (!doc || !doc.hasUnsavedChanges) return

    set({ isSaving: true, saveError: null })

    try {
      const fullContent = buildMarkdownWithFrontmatter(
        doc.content,
        doc.frontmatter
      )

      const result = await updateVaultFile(
        doc.path,
        fullContent,
        doc.sha,
        message
      )

      set({
        document: {
          ...doc,
          sha: result.sha,
          hasUnsavedChanges: false,
          lastSaved: new Date()
        },
        isSaving: false
      })
    } catch (error) {
      if (error.status === 409) {
        // Conflict detected
        set({
          conflictState: {
            localContent: doc.content,
            remoteContent: error.data.current_content,
            remoteSha: error.data.current_sha
          },
          isSaving: false
        })
      } else {
        set({
          saveError: error.message,
          isSaving: false
        })
      }
    }
  },

  // ... otros métodos
}))
```

---

## 4. Plan de Desarrollo

### Fase 0: Preparación (Sprint 0)
**Duración:** 1 semana

**Objetivos:**
- Setup del entorno de desarrollo
- Investigación de librerías
- Prototipo básico de Lexical

**Tareas:**
- [ ] Instalar y configurar Lexical
- [ ] Crear componente básico MarkdownEditor
- [ ] Probar serialización Markdown ↔ Lexical
- [ ] Configurar entorno de testing para editor

**Entregables:**
- Editor básico que carga y muestra contenido
- Documentación de decisiones técnicas

---

### Fase 1: MVP - Edición Básica (Sprint 1-2)
**Duración:** 2 semanas

**Objetivos:**
- Editor funcional con guardar/descartar
- Integración con API de GitHub
- Detección de cambios sin guardar

**Historias de Usuario:**
- US-001: Abrir archivo en modo edición
- US-002: Guardar cambios en GitHub
- US-003: Detectar cambios sin guardar

**Tareas Técnicas:**
- [ ] Implementar MarkdownEditor component
- [ ] Integrar Lexical editor
- [ ] Crear EditorToolbar con botones básicos
- [ ] Implementar SaveIndicator
- [ ] Extender API: PUT /vault/file/content
- [ ] Implementar detección de cambios
- [ ] Agregar confirmación al cerrar con cambios
- [ ] Tests unitarios para serialización

**Entregables:**
- Usuario puede editar y guardar archivos markdown
- Indicadores visuales de estado de guardado

---

### Fase 2: Formato Básico (Sprint 3)
**Duración:** 1 semana

**Objetivos:**
- Atajos de teclado para formato
- Barra de herramientas flotante
- Autocompletado básico

**Historias de Usuario:**
- US-004: Aplicar formato con atajos de teclado
- US-005: Barra de herramientas de formato
- US-006: Autocompletado de sintaxis markdown

**Tareas Técnicas:**
- [ ] Implementar MarkdownShortcutsPlugin
- [ ] Crear FloatingToolbar component
- [ ] Agregar listeners de teclado (Cmd+B, Cmd+I, etc.)
- [ ] Implementar autocompletado de pares (**, [[, etc.)
- [ ] Styling de toolbar
- [ ] Tests de atajos de teclado

**Entregables:**
- Experiencia de formato fluida y rápida
- Toolbar flotante al seleccionar texto

---

### Fase 3: Funcionalidades de Obsidian (Sprint 4-5)
**Duración:** 2 semanas

**Objetivos:**
- Soporte completo para wikilinks
- Tags funcionales
- Preview en tiempo real

**Historias de Usuario:**
- US-007: Soporte para Wikilinks
- US-008: Soporte para Tags
- US-013: Vista previa en tiempo real

**Tareas Técnicas:**
- [ ] Crear WikiLinkNode en Lexical
- [ ] Implementar WikiLinkPlugin
- [ ] Autocompletado de wikilinks (buscar notas)
- [ ] Navegación entre notas vía wikilinks
- [ ] Crear TagNode en Lexical
- [ ] Implementar TagPlugin
- [ ] Crear PreviewPane component
- [ ] Sincronizar scroll entre editor y preview
- [ ] Tests de parsing de wikilinks y tags

**Entregables:**
- Wikilinks y tags funcionan como en Obsidian
- Vista previa en tiempo real sincronizada

---

### Fase 4: Funcionalidades Estilo Notion (Sprint 6-7)
**Duración:** 2 semanas

**Objetivos:**
- Menú de comandos con /
- Menciones con @
- UI moderna y fluida

**Historias de Usuario:**
- US-011: Menú de comandos con /
- US-012: Menciones con @

**Tareas Técnicas:**
- [ ] Implementar SlashCommandPlugin
- [ ] Crear CommandMenu component
- [ ] Agregar comandos: heading, list, code, etc.
- [ ] Implementar MentionPlugin
- [ ] Integrar con búsqueda de notas
- [ ] Animaciones y transiciones suaves
- [ ] Tests de menú de comandos

**Entregables:**
- Experiencia de escritura moderna estilo Notion
- Inserción rápida de bloques con /

---

### Fase 5: Creación de Contenido (Sprint 8)
**Duración:** 1 semana

**Objetivos:**
- Crear nuevas notas desde editor
- Sistema básico de templates

**Historias de Usuario:**
- US-016: Crear nueva nota desde el editor
- US-017: Templates de notas (básico)

**Tareas Técnicas:**
- [ ] Extender API: POST /vault/file/create
- [ ] Crear modal de nueva nota
- [ ] Selector de ubicación (carpetas)
- [ ] Templates predefinidos básicos
- [ ] Variables en templates ({{date}}, {{title}})
- [ ] Tests de creación de archivos

**Entregables:**
- Usuario puede crear notas nuevas
- Templates básicos disponibles

---

### Fase 6: Mejoras de UX (Sprint 9)
**Duración:** 1 semana

**Objetivos:**
- Detección de conflictos
- Auto-guardado
- Modo focus

**Historias de Usuario:**
- US-018: Detección de conflictos
- US-019: Auto-guardado
- US-014: Modo focus

**Tareas Técnicas:**
- [ ] Implementar detección de conflictos (SHA check)
- [ ] Crear ConflictResolver component
- [ ] Implementar AutoSavePlugin
- [ ] Configuración de auto-guardado
- [ ] Implementar modo focus (toggle UI)
- [ ] Tests de detección de conflictos

**Entregables:**
- Sistema robusto de guardado sin pérdida de datos
- Experiencia de escritura sin distracciones

---

### Fase 7: Funcionalidades de IA - Básicas (Sprint 10-11)
**Duración:** 2 semanas

**Objetivos:**
- Asistente de escritura IA (Cmd+K)
- Corrección de inglés en tiempo real
- Generación de contenido básica

**Historias de Usuario:**
- US-020: Asistente de escritura IA
- US-021: Corrección de inglés en tiempo real
- US-022: Generación de contenido con IA

**Tareas Técnicas:**
- [ ] Crear API endpoints en `/api/v1/editor/ai`
- [ ] Implementar AIAssistantPanel component
- [ ] Implementar AIAssistantPlugin en Lexical
- [ ] Crear EnglishCorrectionPlugin
- [ ] Implementar CorrectionMarkNode
- [ ] Crear AICommandMenu para `/ai` commands
- [ ] Integrar con sistema de correcciones existente
- [ ] Tests de integración con LLM

**Entregables:**
- Cmd+K abre asistente IA
- Correcciones de inglés en tiempo real
- Comandos `/ai` funcionales

---

### Fase 8: Funcionalidades de IA - Avanzadas (Sprint 12-13)
**Duración:** 2 semanas

**Objetivos:**
- Generación automática de metadata
- Chat contextual en el editor
- Referencias inteligentes

**Historias de Usuario:**
- US-025: Generación de títulos y resúmenes
- US-026: Chat contextual en el editor
- US-027: Mejora de tono y estilo
- US-028: Referencias inteligentes

**Tareas Técnicas:**
- [ ] Implementar ChatSidebar component
- [ ] Crear ToneAdjuster component
- [ ] Implementar SuggestedLinks panel
- [ ] Integrar con RAG para sugerencias de links
- [ ] Metadata generation use case
- [ ] Tests de calidad de sugerencias

**Entregables:**
- Chat con Dave dentro del editor
- Sugerencias de wikilinks automáticas
- Generación de metadata inteligente

---

### Fase 9: Features Avanzadas Opcionales (Sprint 14+)
**Duración:** Variable (priorizar según feedback)

**Features Opcionales:**
- US-009: Editor de Frontmatter visual
- US-010: Bloques arrastrables
- US-015: Historial de versiones
- US-017: Templates avanzados
- US-023: Autocompletado inteligente con IA
- US-024: Análisis de estructura
- US-029: Detección de duplicados

**Priorización:**
- Según feedback de usuarios
- Métricas de uso
- Complejidad vs valor

---

## 5. Criterios de Éxito

### Métricas de Producto
- [ ] 80% de usuarios activos usan el editor al menos 1 vez/semana
- [ ] Tiempo promedio de edición > 5 minutos (engagement)
- [ ] Tasa de error en guardado < 1%
- [ ] 0 pérdidas de datos reportadas

### Métricas Técnicas
- [ ] Time to Interactive (TTI) del editor < 2 segundos
- [ ] Latencia de guardado < 3 segundos (P95)
- [ ] Cobertura de tests > 80%
- [ ] 0 errores críticos en producción

### Experiencia de Usuario
- [ ] NPS (Net Promoter Score) > 8/10
- [ ] Usuarios pueden completar tareas básicas sin ayuda
- [ ] Feedback positivo sobre fluidez del editor
- [ ] Paridad de features con Obsidian (core features)

---

## 6. Riesgos y Mitigaciones

### Riesgo 1: Pérdida de Datos
**Probabilidad:** Media
**Impacto:** Crítico
**Mitigación:**
- Detección estricta de conflictos
- Auto-guardado frecuente
- Guardado local en localStorage como backup
- Tests exhaustivos de flujos de guardado

### Riesgo 2: Performance con Documentos Grandes
**Probabilidad:** Media
**Impacto:** Alto
**Mitigación:**
- Lazy loading de bloques
- Virtualización de contenido largo
- Debouncing de preview updates
- Tests de performance con docs grandes (>10k líneas)

### Riesgo 3: Incompatibilidad con Markdown de Obsidian
**Probabilidad:** Media
**Impacto:** Alto
**Mitigación:**
- Usar parsers robustos (unified/remark)
- Tests con archivos reales de Obsidian
- Validación de sintaxis antes de guardar
- Modo "raw" como fallback

### Riesgo 4: Rate Limiting de GitHub API
**Probabilidad:** Baja
**Impacto:** Medio
**Mitigación:**
- Implementar retry con exponential backoff
- Cachear contenido localmente
- Batch commits si es posible
- Monitoreo de rate limits

### Riesgo 5: Complejidad de Lexical
**Probabilidad:** Media
**Impacto:** Medio
**Mitigación:**
- Spike inicial de investigación (Sprint 0)
- Prototipo temprano
- Considerar alternativas (TipTap, ProseMirror)
- Documentación interna de patrones

---

## 7. Dependencias y Consideraciones

### Dependencias Externas
- **GitHub API**: Disponibilidad y rate limits
- **Lexical**: Estabilidad de la librería (aún en desarrollo activo)
- **Obsidian**: Compatibilidad con futuras versiones

### Consideraciones de Seguridad
- Validación de markdown (prevenir XSS)
- Sanitización de HTML en preview
- Verificación de permisos de escritura en GitHub
- Rate limiting de requests

### Consideraciones de Accesibilidad
- Editor accesible por teclado
- ARIA labels en botones y controles
- Soporte para lectores de pantalla
- Alto contraste para modo oscuro

---

## 8. Documentación

### Documentación Técnica
- [ ] README de componente MarkdownEditor
- [ ] Guía de creación de plugins de Lexical
- [ ] API de sincronización con GitHub
- [ ] Troubleshooting guide

### Documentación de Usuario
- [ ] Tutorial de primeros pasos
- [ ] Atajos de teclado
- [ ] Guía de wikilinks y tags
- [ ] FAQ

---

## 9. Próximos Pasos

1. **Revisar y aprobar este plan** con stakeholders
2. **Sprint 0**: Investigación y setup (esta semana)
3. **Sprint 1-2**: Comenzar desarrollo del MVP
4. **Demo del MVP**: Al final de Sprint 2
5. **Iterar** basándose en feedback

---

## Apéndice A: Comparación de Librerías de Editor

| Librería | Pros | Contras | Decisión |
|----------|------|---------|----------|
| **Lexical** | Moderno, performante, extensible, React-first | Joven, menos ejemplos | ✅ **Elegida** |
| **TipTap** | Maduro, muchos plugins, buena docs | Basado en ProseMirror (complejo) | Alternativa |
| **ProseMirror** | Muy maduro, poderoso | Curva de aprendizaje alta, no React-first | Descartada |
| **Slate** | React-first, flexible | Performance issues con docs grandes | Descartada |
| **Draft.js** | Usado por Facebook | No mantenido activamente | Descartada |

---

## Apéndice B: Funcionalidades de IA - Ejemplos de Uso

### Ejemplo 1: Asistente de Escritura (Cmd+K)

```
[Texto seleccionado]: "This project is for making better the productivity"

Usuario presiona Cmd+K

┌────────────────────────────────────────────────────┐
│ ✨ Ask AI                                          │
├────────────────────────────────────────────────────┤
│ What do you want to do with this text?            │
│ ┌────────────────────────────────────────────────┐ │
│ │ make it more natural_                          │ │
│ └────────────────────────────────────────────────┘ │
│                                                    │
│ 💡 Suggestion:                                     │
│ "This project aims to improve productivity"       │
│                                                    │
│ 📝 Explanation:                                    │
│ More natural phrasing using "aims to improve"     │
│ instead of "is for making better"                 │
│                                                    │
│ [Accept] [Regenerate] [Edit] [Cancel]             │
└────────────────────────────────────────────────────┘
```

### Ejemplo 2: Corrección de Inglés en Tiempo Real

```
Editor content:
┌──────────────────────────────────────────────────────┐
│ I went to ~the office~ yesterday and I ~have met~   │
│        grammar ──┘               grammar ──┘         │
│ with my colleagues.                                  │
│                                                      │
│ We ~discussed about~ the new project and ~we was~   │
│    naturalness ──┘                  grammar ──┘     │
│ very excited.                                        │
└──────────────────────────────────────────────────────┘

Hover sobre "the office":
┌─────────────────────────────────────┐
│ ❌ Article unnecessary               │
│                                     │
│ Suggestion: "office" or "my office" │
│                                     │
│ In this context, "the office"      │
│ sounds formal. Native speakers      │
│ often say "I went to work" or just  │
│ "to the office" without "the"       │
│                                     │
│ [Apply Fix] [Ignore]                │
└─────────────────────────────────────┘

Sidebar panel:
┌──────────────────────────────┐
│ 📝 English Corrections (4)   │
├──────────────────────────────┤
│ ⚠️ Grammar (2)               │
│ • "the office" → "office"    │
│ • "have met" → "met"         │
│ • "we was" → "we were"       │
│                              │
│ 💬 Naturalness (1)           │
│ • "discussed about" →        │
│   "discussed"                │
│                              │
│ [Apply All] [Clear]          │
└──────────────────────────────┘
```

### Ejemplo 3: Comandos /ai

```
Usuario escribe: /ai

┌─────────────────────────────────────────┐
│ 🤖 AI Commands                          │
├─────────────────────────────────────────┤
│ /ai generate     Generate content       │
│ /ai summarize    Summarize text         │
│ /ai expand       Expand bullet points   │
│ /ai brainstorm   Generate ideas         │
│ /ai translate    Translate to English   │
│ /ai tone         Change tone/style      │
└─────────────────────────────────────────┘

Usuario selecciona "/ai generate":

┌─────────────────────────────────────────┐
│ ✨ Generate Content                     │
├─────────────────────────────────────────┤
│ Topic:                                  │
│ ┌─────────────────────────────────────┐ │
│ │ AI in healthcare_                   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Style: [Professional ▼]                │
│ Length: [Medium ▼]                     │
│                                         │
│ [Generate]                              │
└─────────────────────────────────────────┘

Resultado:
# AI in Healthcare

Artificial Intelligence is revolutionizing healthcare
through several key applications:

1. **Diagnostic Support**: AI algorithms can analyze
   medical images with high accuracy...

2. **Personalized Treatment**: Machine learning models
   help predict patient responses...

[Keep] [Regenerate] [Edit]
```

### Ejemplo 4: Chat Contextual con Dave

```
┌────────────────────────────────────────────────────────────┐
│ Editor                          │ 💬 Chat with Dave        │
├─────────────────────────────────┼──────────────────────────┤
│ # Project Planning              │                          │
│                                 │ 👤 You:                  │
│ ## Goals                        │ What else should I       │
│ - Improve user onboarding       │ include in this plan?    │
│ - Reduce churn rate             │                          │
│                                 │ 🤖 Dave:                 │
│ ## Timeline                     │ Based on your goals,     │
│ Q1 2024: Research phase         │ I'd suggest adding:      │
│                                 │                          │
│ _                               │ 1. Success metrics       │
│                                 │    (KPIs for each goal)  │
│                                 │                          │
│                                 │ 2. Risk assessment       │
│                                 │    section               │
│                                 │                          │
│                                 │ 3. Resource allocation   │
│                                 │                          │
│                                 │ I also found a related   │
│                                 │ note: [[Product Roadmap]]│
│                                 │                          │
│                                 │ [Insert suggestions]     │
└─────────────────────────────────┴──────────────────────────┘
```

### Ejemplo 5: Sugerencias Inteligentes de Links

```
┌──────────────────────────────────────────────────────────┐
│ # Meeting Notes - Team Sync                              │
│                                                          │
│ We discussed the new authentication system with          │
│ John and decided to use OAuth 2.0 for the implementation.│
│                                                          │
│ Next steps: Review the API documentation and setup      │
│ the development environment.                             │
└──────────────────────────────────────────────────────────┘

Sidebar automático:
┌─────────────────────────────────────┐
│ 🔗 Suggested Links                  │
├─────────────────────────────────────┤
│ Based on your content:              │
│                                     │
│ 📄 [[John Smith]] - Person          │
│    "...senior engineer working on..." │
│    [Insert link]                    │
│                                     │
│ 📄 [[OAuth Implementation]] - Note  │
│    "...guide for setting up OAuth..." │
│    [Insert link]                    │
│                                     │
│ 📄 [[API Documentation]] - Resource │
│    "...comprehensive API docs for..." │
│    [Insert link]                    │
│                                     │
│ 📄 [[Dev Environment Setup]] - How-to│
│    "...step by step guide for..."    │
│    [Insert link]                    │
└─────────────────────────────────────┘
```

---

## Apéndice C: Wireframes Básicos

### Vista de Editor
```
┌──────────────────────────────────────────────────────┐
│ [🏠] [📁] vault/notes/my-note.md        [💾 Save]   │ <- Header
├──────────────────────────────────────────────────────┤
│ [B] [I] [Code] [Link] [Image]    [👁️ Preview] [⚙️]  │ <- Toolbar
├────────────────────────┬─────────────────────────────┤
│                        │                             │
│   # My Note            │   My Note                  │
│                        │   =========                 │
│   This is **bold**     │   This is bold text        │
│   and this is normal.  │   and this is normal.      │
│                        │                             │
│   - List item 1        │   • List item 1            │
│   - List item 2        │   • List item 2            │
│                        │                             │
│   [[wikilink]]         │   wikilink (link)          │
│   #tag                 │   #tag (styled)            │
│                        │                             │
│   Editor               │   Preview                   │
│                        │                             │
└────────────────────────┴─────────────────────────────┘
```

### Floating Toolbar (al seleccionar texto)
```
    texto seleccionado aquí
    ┌──────────────────────┐
    │ B  I  U  `  🔗  🎨   │ <- Aparece arriba del texto
    └──────────────────────┘
```

### Command Menu (al escribir /)
```
    /
    ┌────────────────────────┐
    │ 🔍 Type to search...   │
    ├────────────────────────┤
    │ # Heading              │
    │ - Bullet list          │
    │ ☑️ Checkbox list       │
    │ ``` Code block         │
    │ --- Divider            │
    │ 📊 Table               │
    └────────────────────────┘
```

---

**Última actualización:** 2025-11-26
**Autor:** Claude (Dave AI)
**Estado:** Borrador para revisión
