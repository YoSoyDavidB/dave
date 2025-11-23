---
created: 2024-11-22
tags:
  - project
  - AI
  - user-stories
status: draft
---

# 📋 Dave - User Stories

---

## Epic 1: Core Chat Experience

### US-1.1: Basic Conversation
**As a** user
**I want to** have a natural conversation with Dave
**So that** I can interact in a friendly, casual way

**Acceptance Criteria:**
- [ ] Can send text messages
- [ ] Receives responses within 3 seconds
- [ ] Responses feel natural and friendly (not robotic)
- [ ] Conversation history is visible
- [ ] Can start new conversations

**Story Points:** 5

---

### US-1.2: Streaming Responses
**As a** user
**I want to** see Dave's response appear word by word
**So that** I don't have to wait for the full response

**Acceptance Criteria:**
- [ ] Response streams in real-time (like ChatGPT)
- [ ] Typing indicator shows when Dave is "thinking"
- [ ] Can see partial response while still generating

**Story Points:** 3

---

### US-1.3: Personality & Tone
**As a** user
**I want** Dave to feel like a close friend
**So that** interactions are enjoyable and I want to keep using it

**Acceptance Criteria:**
- [ ] Uses casual language
- [ ] Includes appropriate humor
- [ ] Shows genuine interest (asks follow-up questions)
- [ ] Celebrates wins, supports during struggles
- [ ] Remembers context from earlier in conversation

**Story Points:** 3

---

## Epic 2: English Correction

### US-2.1: Grammar Correction
**As a** English learner
**I want** Dave to correct my grammar mistakes
**So that** I can improve my English accuracy

**Acceptance Criteria:**
- [ ] Detects grammar errors (verb tense, articles, prepositions)
- [ ] Shows correction at end of Dave's response
- [ ] Correction is friendly, not judgmental
- [ ] Shows original → corrected format

**Story Points:** 5

---

### US-2.2: Natural Phrasing Suggestions
**As a** English learner
**I want** suggestions to sound more natural
**So that** I don't sound like a textbook

**Acceptance Criteria:**
- [ ] Identifies correct-but-unnatural phrasing
- [ ] Suggests more native-like alternatives
- [ ] Explains why the suggestion sounds better
- [ ] Only suggests when there's a meaningful difference

**Story Points:** 5

---

### US-2.3: Error Explanations
**As a** English learner
**I want** brief explanations of why something is wrong
**So that** I understand and don't repeat the mistake

**Acceptance Criteria:**
- [ ] Each correction includes a brief explanation
- [ ] Explanations are clear and simple
- [ ] Uses examples when helpful
- [ ] Not overwhelming (max 2-3 sentences)

**Story Points:** 3

---

### US-2.4: Progress Tracking
**As a** English learner
**I want** to see my progress over time
**So that** I stay motivated

**Acceptance Criteria:**
- [ ] Tracks errors by category (grammar, naturalness, vocabulary)
- [ ] Shows most common mistakes
- [ ] Shows streak of days practiced
- [ ] Can see improvement over time

**Story Points:** 5

---

### US-2.5: Repeated Error Detection
**As a** English learner
**I want** Dave to notice when I repeat the same mistake
**So that** I can focus on fixing it

**Acceptance Criteria:**
- [ ] Tracks which errors I make repeatedly
- [ ] Mentions when I make the same error again
- [ ] Suggests practice exercises for common errors
- [ ] Celebrates when I stop making a recurring error

**Story Points:** 3

---

## Epic 3: Obsidian Integration

### US-3.1: Create Daily Note
**As a** user
**I want** Dave to create my daily note from our conversation
**So that** I don't have to manually write it

**Acceptance Criteria:**
- [ ] Can ask Dave to create today's daily note
- [ ] Extracts relevant info from conversation (tasks, notes, mood)
- [ ] Uses correct template format
- [ ] Saves to correct path (Timestamps/YYYY/MM-Month/)
- [ ] Confirms creation with link to note

**Story Points:** 8

---

### US-3.2: Create Person Note
**As a** user
**I want** Dave to create a note when I mention a new person
**So that** I build my personal CRM automatically

**Acceptance Criteria:**
- [ ] Recognizes when I mention a new person
- [ ] Asks for relevant details (how I met them, company, etc.)
- [ ] Creates note using People template
- [ ] Saves to Extras/People/
- [ ] Links person to relevant meetings/notes

**Story Points:** 5

---

### US-3.3: Add Tasks
**As a** user
**I want** Dave to extract tasks from our conversation
**So that** I don't forget things I mentioned

**Acceptance Criteria:**
- [ ] Recognizes task-like statements ("I need to...", "I should...")
- [ ] Asks for confirmation before creating tasks
- [ ] Adds tasks to daily note or specific project note
- [ ] Sets due dates if mentioned

**Story Points:** 5

---

### US-3.4: Search Notes
**As a** user
**I want** to ask Dave questions about my notes
**So that** I can find information without manual searching

**Acceptance Criteria:**
- [ ] Can search by keyword
- [ ] Can search by semantic meaning (RAG)
- [ ] Returns relevant excerpts from notes
- [ ] Links to full notes

**Story Points:** 8

---

### US-3.5: PARA Organization
**As a** user
**I want** Dave to organize notes following PARA method
**So that** my vault stays organized

**Acceptance Criteria:**
- [ ] Understands PARA categories (Projects, Areas, Resources, Archive)
- [ ] Suggests correct location for new notes
- [ ] Can explain why a note belongs somewhere
- [ ] Follows my existing folder structure

**Story Points:** 3

---

## Epic 4: Proactive Features

### US-4.1: Task Reminders
**As a** user
**I want** Dave to remind me of pending tasks
**So that** I don't forget important things

**Acceptance Criteria:**
- [ ] Reads tasks from daily notes
- [ ] Reminds me of overdue tasks
- [ ] Suggests prioritization
- [ ] Doesn't spam - smart timing

**Story Points:** 5

---

### US-4.2: Weekly Review Prompt
**As a** user
**I want** Dave to prompt me for weekly review
**So that** I maintain my productivity system

**Acceptance Criteria:**
- [ ] Suggests weekly review on Sundays
- [ ] Helps guide through review process
- [ ] Summarizes the week's accomplishments
- [ ] Helps plan next week

**Story Points:** 5

---

### US-4.3: Therapy Autoregistro
**As a** user
**I want** Dave to help me create autoregistros
**So that** I maintain my therapy practice

**Acceptance Criteria:**
- [ ] Can trigger autoregistro creation
- [ ] Guides through situation → emotion → thought
- [ ] Uses correct template
- [ ] Saves to Area/Terapia/Autoregistros/

**Story Points:** 3

---

## Epic 5: Calendar Integration (Phase 2)

### US-5.1: View Calendar
**As a** user
**I want** to ask Dave about my schedule
**So that** I can plan my day

**Acceptance Criteria:**
- [ ] Can query today's/tomorrow's/this week's events
- [ ] Shows time, title, and location
- [ ] Works with Google Calendar
- [ ] Works with Outlook Calendar

**Story Points:** 5

---

### US-5.2: Create Events
**As a** user
**I want** Dave to create calendar events from conversation
**So that** I don't have to switch apps

**Acceptance Criteria:**
- [ ] Extracts event details from conversation
- [ ] Asks for confirmation
- [ ] Creates event in selected calendar
- [ ] Handles time zones correctly

**Story Points:** 5

---

## Epic 6: Email Integration (Phase 2)

### US-6.1: Email Summary
**As a** user
**I want** Dave to summarize my recent emails
**So that** I stay on top of communication

**Acceptance Criteria:**
- [ ] Can query recent emails
- [ ] Shows sender, subject, and brief summary
- [ ] Highlights urgent/important emails
- [ ] Works with Gmail and Outlook

**Story Points:** 5

---

### US-6.2: Draft Email
**As a** user
**I want** Dave to help me draft email replies
**So that** I can respond faster

**Acceptance Criteria:**
- [ ] Can reference a specific email
- [ ] Generates draft based on my instructions
- [ ] Matches my writing style
- [ ] Can iterate on draft

**Story Points:** 5

---

## Epic 7: WhatsApp Bot (Phase 2)

### US-7.1: WhatsApp Access
**As a** user
**I want** to chat with Dave via WhatsApp
**So that** I can access it from my phone easily

**Acceptance Criteria:**
- [ ] Can send messages via WhatsApp
- [ ] Receives responses in WhatsApp
- [ ] All features available (not just text)
- [ ] Same conversation history as web

**Story Points:** 8

---

## Story Map

```
                    MVP (Phase 1)                    │       Phase 2          │  Phase 3
                                                     │                        │
┌────────────────────────────────────────────────────┼────────────────────────┼──────────┐
│                                                    │                        │          │
│  US-1.1 Basic Chat ──▶ US-1.2 Streaming           │                        │          │
│         │                                          │                        │          │
│         ▼                                          │                        │          │
│  US-1.3 Personality                                │                        │          │
│                                                    │                        │          │
├────────────────────────────────────────────────────┤                        │          │
│                                                    │                        │          │
│  US-2.1 Grammar ──▶ US-2.2 Natural ──▶ US-2.3 Exp │  US-2.4 Progress      │          │
│                                          │         │         │              │          │
│                                          └─────────┼──▶ US-2.5 Repeated    │          │
│                                                    │                        │          │
├────────────────────────────────────────────────────┤                        │          │
│                                                    │                        │          │
│  US-3.1 Daily Note                                 │                        │          │
│         │                                          │                        │          │
│         ├──▶ US-3.2 Person Note                    │                        │          │
│         │                                          │                        │          │
│         ├──▶ US-3.3 Tasks                          │                        │          │
│         │                                          │                        │          │
│         └──▶ US-3.4 Search (RAG)                   │                        │          │
│                    │                               │                        │          │
│                    └──▶ US-3.5 PARA                │                        │          │
│                                                    │                        │          │
├────────────────────────────────────────────────────┤                        │          │
│                                                    │                        │          │
│  US-4.1 Reminders ──▶ US-4.2 Weekly Review        │                        │          │
│         │                                          │                        │          │
│         └──▶ US-4.3 Autoregistro                   │                        │          │
│                                                    │                        │          │
├────────────────────────────────────────────────────┼────────────────────────┤          │
│                                                    │                        │          │
│                                                    │  US-5.1 View Calendar  │          │
│                                                    │         │              │          │
│                                                    │         └▶ US-5.2 Create│         │
│                                                    │                        │          │
│                                                    │  US-6.1 Email Summary  │          │
│                                                    │         │              │          │
│                                                    │         └▶ US-6.2 Draft│          │
│                                                    │                        │          │
│                                                    │  US-7.1 WhatsApp       │          │
│                                                    │                        │          │
└────────────────────────────────────────────────────┴────────────────────────┴──────────┘
```

---

## Priority Matrix

| Story | Value | Effort | Priority |
|-------|-------|--------|----------|
| US-1.1 Basic Chat | High | Medium | P0 |
| US-1.2 Streaming | Medium | Low | P1 |
| US-1.3 Personality | High | Low | P0 |
| US-2.1 Grammar | High | Medium | P0 |
| US-2.2 Natural | High | Medium | P1 |
| US-2.3 Explanations | Medium | Low | P1 |
| US-2.4 Progress | Medium | Medium | P2 |
| US-3.1 Daily Note | High | High | P0 |
| US-3.2 Person Note | Medium | Medium | P1 |
| US-3.3 Tasks | High | Medium | P1 |
| US-3.4 Search | High | High | P1 |
| US-4.1 Reminders | Medium | Medium | P2 |
| US-5.1 Calendar | Medium | Medium | P2 |
| US-7.1 WhatsApp | High | High | P2 |

---

## Definition of Done

A user story is complete when:

- [ ] Code is written and follows project conventions
- [ ] Unit tests pass (>80% coverage for new code)
- [ ] Integration tests pass (if applicable)
- [ ] Code reviewed and approved
- [ ] Documentation updated (if needed)
- [ ] Feature works in staging environment
- [ ] No known bugs
- [ ] Product owner accepts the feature
