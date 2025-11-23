---
created: 2024-11-22
tags:
  - project
  - AI
  - english
status: draft
---

# 🤖 English AI Agent - Design Questions

> Responde estas preguntas para definir el documento de diseño del proyecto.
> Puedes responder en español o inglés (o mezclado).

---

## 1. Alcance y visión

### ¿Este agente viviría dentro de Obsidian (como plugin) o sería una app externa que se conecta a tu vault?

**Respuesta:**
será una app externa que se conecta a mi Vault, el vault se sincroniza cada 5 minutos con un repositorio de github (hace push y pull automáticamente)
### ¿Lo imaginas como CLI, app de escritorio, extensión de VS Code, bot de Telegram/WhatsApp, o interfaz web?

**Respuesta:**
lo estaba imaginando como una web app (por que es mi área de mas experiencia) pero también me parece buena idea que sea un bot de Whatsapp por que es más accesible.
### ¿Solo para ti o eventualmente lo compartirías/monetizarías?

**Respuesta:**
Inicialmente sería solo para mí pero quiero construirlo de manera que pueda ser compartido/monetizado (nunca se sabe y tal vez pueda sacar algún beneficio de esta idea)

---

## 2. Interacción

### ¿Cómo te imaginas la interacción?

- [ ] Yo inicio la conversación
- [ ] El agente me "busca" (notificaciones, recordatorios)
- [x] Ambos

### ¿Conversación tipo chat o más como comandos/acciones?

**Respuesta:**
Tipo chat para que sea una interacción más natura, en el futuro también podría pensar en incluir funcionalidad de voz para que sea una interacción más natural 

### ¿Quieres que el agente tenga "personalidad" (nombre, tono específico)?

**Respuesta:**
absolutamente, me parece fundamental que tenga personalidad, me gusta mucho cuando los agentes me tratan de manera cercana, con humor y a veces un tono burlón, como si fueramos amigos de toda la vida.

---

## 3. Funcionalidades de productividad

### ¿Qué acciones debería poder hacer el agente en tu vault?

- [x] Crear Daily Notes
- [x] Crear notas de reuniones
- [x] Agregar tareas
- [ ] Mover archivos
- [x] Buscar información en notas existentes
- [x] Recordarte tareas pendientes
- [x] Sugerir Weekly Review
- [x] Crear autoregistros de terapia
- [ ] Otras: ___

### ¿Hay alguna funcionalidad de productividad específica que te gustaría?

**Respuesta:**
Me gustaría poder gestionar mi calendario personal y profesional (gmail/outlook). generación de drafts de correos electrónicos, busqueda en internet y acceso una base de datos vectorial para funcionalidades de RAG, esto último sería orientado a poder guardar documentos como manuales de lectrodomesticos, facturas, documentos técnicos  de mi trabajo, etc...

---

## 4. Funcionalidades de inglés

### ¿Cómo debería corregirte?

- [ ] Inline mientras escribes => esto me parece interesante, pero me da miedo que llegue a ser muy intrusivo.
- [x] Al final de cada mensaje
- [ ] Solo si se lo pido
- [ ] Otro: ___

### ¿Qué nivel de corrección?

- [ ] Solo errores gramaticales
- [ ] También sugerencias de "sonar más natural"
- [ ] Explicaciones de por qué algo está mal
- [x] Todo lo anterior

### ¿Debería trackear tu progreso?

- [x] Errores frecuentes que cometo
- [x] Palabras nuevas que aprendo
- [x] Streak de días practicando
- [x] Estadísticas de mejora
- [ ] Otro: ___

---

## 5. Sobre la "sutileza"

### Cuando dices "sutil", ¿te refieres a qué exactamente?

- [ ] Que no sea molesto/intrusivo
- [x] Que las correcciones estén integradas naturalmente en la conversación
- [ ] Que me corrija sin hacerme sentir mal
- [ ] Otro: ___

### ¿Tienes algún ejemplo de cómo te gustaría que se sintiera la interacción?

**Respuesta:**
divertida enganchadora, que sea como una conversación natural entre 2 buenos amigos que se cuentan todo con mucha confianza

---

## 6. Stack tecnológico preferido

### ¿Tienes preferencia de lenguaje de programación?

- [x] TypeScript/JavaScript
- [x] Python
- [ ] Go
- [ ] Rust
- [ ] No tengo preferencia
- [ ] Otro: ___
- [x] Me gusta Python para el backend y TypeScript/Javascript para el front

### ¿Qué LLM prefieres?

- [ ] OpenAI (GPT-4)
- [ ] Claude API (Anthropic)
- [ ] Local con Ollama
- [ ] Múltiples (fallback)
- [ ] No tengo preferencia
- [x] Otro: tengo una cuenta de openrouter que creo que puede venir bien, pero estoy abierto a otras posibilidades

### ¿Ya tienes API keys o presupuesto estimado para costos de API?

**Respuesta:**
Tengo una cuenta de openrouter y una suscripción de clude code

---

## 7. Integraciones

### ¿Debería integrarse con algo más además de Obsidian?

- [x] Google Calendar
- [x] Outlook Calendar
- [x] Todoist
- [ ] Things => no se que es ni para que sirve esto
- [ ] Apple Reminders
- [ ] Slack
- [ ] Teams
- [ ] Telegram
- [x] WhatsApp
- [ ] Ninguna por ahora
- [ ] Otras: ___

---

## 8. Almacenamiento y memoria

### ¿El contexto/memoria del agente debería persistir entre sesiones?

- [x] Sí, debería recordar conversaciones anteriores
- [ ] Sí, pero solo información relevante (errores, progreso, preferencias)
- [ ] No, cada conversación es independiente

### ¿Dónde guardarías esa memoria?

- [ ] En el mismo vault de Obsidian (como notas)
- [ ] Base de datos externa (SQLite, PostgreSQL, etc.)
- [x] Vector database (para RAG)
- [x] Otro: Tengo en mi homelab contenedores de neo4j y Qdrant

---

## 9. Infraestructura

### ¿Dónde lo correrías?

- [ ] Localmente en mi Mac
- [ ] En mi HomeLab
- [ ] En la nube (Vercel, Railway, etc.)
- [ ] Híbrido (local + cloud)
- [x] cloud
Nota: también tengo desplegada una instancia de N8N (por si fuese de utilidad para algún tipo de automatización, integraciones o uso de agentes de IA)
### ¿Tienes preferencia de hosting?

**Respuesta:**
Tengo una VPS desplegada en Hostigner

---

## 10. Proceso de desarrollo

### ¿Cuánto tiempo puedes dedicarle semanalmente?

- [ ] 1-2 horas
- [ ] 3-5 horas
- [x] 5-10 horas
- [ ] Más de 10 horas

### ¿Prefieres empezar con un MVP mínimo funcional o planificar todo antes?

- [ ] MVP primero, iterar después
- [x] Planificar bien antes de codear
- [ ] Balance entre ambos

### ¿Quieres usar TDD estricto desde el inicio?

- [x] Sí, tests primero siempre (Ten en cuenta que quiero incluir tests pero no tengo experiencia, usaría este proyecto para aprender todo sobre tests)
- [ ] Tests para funcionalidades críticas
- [ ] Tests después del MVP
- [ ] No es prioridad

---

## 11. Preguntas adicionales

### ¿Hay algo más que quieras agregar sobre cómo imaginas este proyecto?

**Respuesta:**
Su función principal sería ayudarme a crear las daily notes de manera más conversacional, después de la conversación, el agente creará las notas correspondientes en obsidian (daily note, personas o entidades nuevas, notas en general guardadas en el lugar correcto siguiento el método PARA)

### ¿Tienes algún proyecto o herramienta existente que te inspire?

**Respuesta:**
hace un tiempo estuve trabajando en un proyecto llamado AION, puedes ver su documentación en mi vault de obisdian en Projects/Personal/AION. Creo que se puede sacar algunas cosas de allí

---

## Próximos pasos

Una vez respondidas estas preguntas, crearemos:
1. [ ] Documento de diseño (PRD)
2. [ ] Arquitectura técnica
3. [ ] User stories
4. [ ] Plan de desarrollo (fases/sprints)
5. [ ] Setup del repositorio
