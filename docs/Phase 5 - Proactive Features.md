# Phase 5: Proactive Features

**Status:** In Progress
**Timeline:** Weeks 12-13
**Goal:** Make Dave proactively helpful by surfacing insights, reminders, and progress tracking

---

## Overview

Dave should be more than reactive - it should proactively help users stay on track with their goals, remind them of important tasks, and surface relevant insights from their knowledge base.

### Current State (Already Implemented)
✅ Task reminders with notifications bell
✅ Goal tracking with progress slider
✅ Automatic task completion sync from vault
✅ Vault documents visualization in Knowledge Base

### What's Missing (Phase 5 Scope)
- ✅ **Daily/Weekly Insights** - Proactive summaries of progress and activity
- ✅ **Progress Dashboard** - Visual dashboard showing goals, tasks, and progress over time
- 🔲 **Smart Suggestions** - Context-aware suggestions based on current work (partial - LLM generates suggestions in daily summary)
- 🔲 **Habit Tracking** - Track recurring activities and provide streaks/analytics
- 🔲 **Focus Mode** - Suggest focus sessions based on pending tasks
- 🔲 **Contextual Nudges** - Gentle reminders based on conversation context

---

## Sprint 5.1: Daily Insights (Week 12) ✅ COMPLETED

**Goal:** Dave generates daily/weekly summaries of activity, progress, and insights

### User Stories

**US-5.1.1**: ✅ Como usuario, quiero recibir un resumen diario de mi progreso en tareas y goals
**US-5.1.2**: ✅ Como usuario, quiero ver insights sobre mi productividad y patrones de trabajo
**US-5.1.3**: ✅ Como usuario, quiero que Dave me sugiera acciones basadas en mis metas

### Features

#### 1. Daily Summary Generation ✅

**Implementation:**
```python
# backend/src/domain/entities/daily_summary.py
class DailySummary(BaseModel):
    summary_id: UUID
    user_id: str
    date: date
    # Task metrics
    tasks_completed: int
    tasks_created: int
    tasks_pending: int
    # Goal metrics
    goals_updated: list[str]
    goals_progress_delta: float
    # Conversation metrics
    conversations_count: int
    messages_sent: int
    # English learning metrics
    english_corrections: int
    # Productivity score (0-100)
    productivity_score: float
    # AI-generated insights
    top_topics: list[str]
    key_achievements: list[str]
    suggestions: list[str]
    summary_text: str
```

**Backend Tasks:**
- ✅ Create `insights.py` use case with `generate_daily_summary(user_id, date)`
- ✅ LLM prompt to analyze day's conversations + tasks/goals
- ✅ Calculate productivity metrics (completion rate, active hours)
- ✅ Extract top topics from conversations using LLM
- ✅ Generate 3-5 personalized suggestions based on context
- ✅ Store summaries in PostgreSQL for history
- ✅ Create API endpoints for retrieving and generating summaries
  - `GET /api/v1/dashboard/stats` - Comprehensive dashboard stats
  - `GET /api/v1/dashboard/summary/today` - Today's summary
  - `GET /api/v1/dashboard/summary/{date}` - Summary by date
  - `GET /api/v1/dashboard/summary/week` - Week summaries
  - `POST /api/v1/dashboard/summary/generate` - Manual generation
- ✅ Add scheduled job to auto-generate summaries at 23:00 daily

**Frontend Tasks:**
- ✅ Create `Dashboard` page (`/dashboard`)
- ✅ Daily summary card component with glass-card design
- ✅ Weekly view with trend charts
- ✅ Productivity score visualization
- ✅ Suggestions list with modern UI
- ✅ Stat cards showing week metrics
- ✅ Generate summary button
- ✅ Loading and error states

**Key Files Created/Modified:**
- `backend/src/domain/entities/daily_summary.py` - Domain entity
- `backend/src/application/use_cases/insights.py` - Business logic
- `backend/src/api/routes/dashboard.py` - API endpoints
- `backend/src/core/models.py` - DailySummaryModel
- `backend/src/infrastructure/scheduler.py` - Scheduled jobs
- `frontend/src/pages/Dashboard.tsx` - Dashboard UI
- `frontend/src/services/api.ts` - API functions

#### 2. Weekly Insights Email/Notification

**Backend Tasks:**
- [ ] Scheduled job (APScheduler) to generate weekly summaries every Sunday
- [ ] Email template for weekly insights (if user has email configured)
- [ ] In-app notification for weekly summary ready

**Frontend Tasks:**
- [ ] Weekly insights modal/page
- [ ] Comparison charts (this week vs last week)
- [ ] Goal progress over time (line chart)

---

## Sprint 5.2: Smart Suggestions & Focus Mode (Week 12-13)

**Goal:** Dave proactively suggests actions and helps users focus

### User Stories

**US-5.2.1**: Como usuario, quiero que Dave me sugiera qué hacer cuando estoy bloqueado
**US-5.2.2**: Como usuario, quiero iniciar sesiones de "focus mode" para tareas específicas
**US-5.2.3**: Como usuario, quiero que Dave me recuerde tomar descansos durante focus sessions

### Features

#### 1. Contextual Suggestions

Dave analyzes current context and suggests next actions:

```python
@dataclass
class Suggestion:
    suggestion_id: str
    type: str  # "task", "goal_update", "vault_review", "break"
    title: str
    description: str
    priority: int  # 1-5
    context: str  # Why this suggestion was made
    action_url: str | None  # Deep link to action
```

**Suggestion Types:**
- **Task-based**: "You have 3 overdue tasks. Want to tackle them?"
- **Goal-based**: "Your 'Learn Rust' goal hasn't been updated in 2 weeks"
- **Vault-based**: "You took notes on X last week - want to review?"
- **Health-based**: "You've been working for 3 hours - take a break?"
- **Learning-based**: "You made 5 English mistakes with 'its/it's' - review?"

**Backend Tasks:**
- [ ] Suggestion engine that runs every hour (APScheduler)
- [ ] LLM-powered context analysis
- [ ] Priority scoring algorithm
- [ ] Store suggestions in memory with TTL (24h)
- [ ] API endpoint `GET /api/v1/proactive/suggestions`

**Frontend Tasks:**
- [ ] Suggestions panel in dashboard
- [ ] Suggestion cards with dismiss/snooze/act buttons
- [ ] Notification dot when new suggestions available

#### 2. Focus Mode

**Backend Tasks:**
- [ ] Focus session entity (start_time, end_time, task_id, completed)
- [ ] Start/stop focus session endpoints
- [ ] Track time spent on tasks
- [ ] Pomodoro timer logic (25 min work / 5 min break)

**Frontend Tasks:**
- [ ] Focus mode UI (modal or dedicated page)
- [ ] Timer display with progress circle
- [ ] Task selection dropdown
- [ ] Break reminders (toast notifications)
- [ ] Focus session history

---

## Sprint 5.3: Progress Dashboard (Week 13)

**Goal:** Visual dashboard showing comprehensive progress tracking

### User Stories

**US-5.3.1**: Como usuario, quiero ver un dashboard con todos mis goals y su progreso
**US-5.3.2**: Como usuario, quiero ver gráficas de mi productividad a lo largo del tiempo
**US-5.3.3**: Como usuario, quiero ver stats sobre mi uso de Dave (conversaciones, tareas, etc)

### Features

#### 1. Comprehensive Dashboard

**Sections:**
1. **Overview Cards**
   - Tasks completed this week
   - Active goals
   - Productivity score
   - Total conversations

2. **Goals Section**
   - Visual progress bars for each goal
   - Timeline view of goal updates
   - Goal completion history

3. **Tasks Section**
   - Upcoming tasks (next 7 days)
   - Overdue tasks (red)
   - Completed tasks (green checkmark)
   - Task completion rate chart

4. **Activity Heatmap**
   - GitHub-style contribution graph
   - Shows daily activity (conversations, tasks completed)

5. **English Progress**
   - Integration with existing `/learn` page stats
   - Most common mistake types
   - Improvement trend

**Backend Tasks:**
- [ ] Aggregation queries for dashboard stats
- [ ] Cache dashboard data (Redis, 5 min TTL)
- [ ] API endpoint `GET /api/v1/dashboard/stats`

**Frontend Tasks:**
- [ ] Dashboard layout with responsive grid
- [ ] Chart components (recharts library)
- [ ] Activity heatmap component
- [ ] Goal cards with progress animations
- [ ] Real-time updates via polling or WebSocket

---

## Sprint 5.4: Habit Tracking (Optional - if time permits)

**Goal:** Track recurring activities and provide streaks/analytics

### Features

- Track habits (e.g., "Write daily note", "Exercise", "Read")
- Streak counter
- Habit completion heatmap
- Reminders for habits

---

## Technical Architecture

### Backend Structure

```
backend/src/
├── application/use_cases/
│   ├── insights.py          # Daily/weekly summary generation
│   ├── suggestions.py       # Smart suggestion engine
│   └── focus_sessions.py    # Focus mode logic
├── api/routes/
│   └── dashboard.py         # Dashboard stats API
├── infrastructure/
│   └── scheduler.py         # Background jobs (already exists)
└── domain/entities/
    ├── focus_session.py     # Focus session model
    └── suggestion.py        # Suggestion model
```

### Frontend Structure

```
frontend/src/
├── pages/
│   └── Dashboard.tsx        # Main dashboard page
├── components/
│   ├── dashboard/
│   │   ├── DailySummaryCard.tsx
│   │   ├── GoalsProgress.tsx
│   │   ├── ActivityHeatmap.tsx
│   │   ├── TasksOverview.tsx
│   │   └── SuggestionsPanel.tsx
│   └── focus/
│       └── FocusTimer.tsx
└── stores/
    └── dashboardStore.ts
```

### Database Schema

```sql
-- Daily summaries table
CREATE TABLE daily_summaries (
    id UUID PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    date DATE NOT NULL,
    tasks_completed INT,
    tasks_pending INT,
    productivity_score FLOAT,
    top_topics JSONB,
    suggestions JSONB,
    created_at TIMESTAMP,
    UNIQUE(user_id, date)
);

-- Focus sessions table
CREATE TABLE focus_sessions (
    id UUID PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    task_id VARCHAR,  -- Reference to memory with type=TASK
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_minutes INT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);

-- Suggestions table (optional - can use memory system)
CREATE TABLE suggestions (
    id UUID PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    description TEXT,
    priority INT,
    context TEXT,
    action_url VARCHAR,
    dismissed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    expires_at TIMESTAMP
);
```

---

## Implementation Priority

### 🔥 High Priority (Week 12)
1. Daily summary generation (backend + frontend)
2. Dashboard page with stats
3. Smart suggestions engine
4. Suggestions panel in UI

### 🟡 Medium Priority (Week 13)
1. Weekly insights
2. Focus mode with timer
3. Activity heatmap
4. Goal progress visualizations

### 🟢 Low Priority (Nice to have)
1. Habit tracking
2. Email notifications
3. Advanced analytics
4. Export data to CSV

---

## Success Metrics

- [ ] Users check dashboard at least once per day
- [ ] 70%+ of suggestions are acted upon or dismissed (not ignored)
- [ ] Users complete at least 1 focus session per day
- [ ] Daily summary generation takes < 2 seconds
- [ ] Dashboard loads in < 1 second

---

## Next Steps

1. ✅ Create this planning document
2. ✅ Implement daily summary generation (backend)
3. ✅ Create dashboard page (frontend)
4. ✅ Implement suggestion engine (via LLM in daily summary)
5. ⬜ Add focus mode
6. ⬜ Polish and test
7. ⬜ Update main Development Plan

## Implementation Notes

### Productivity Score Algorithm
The productivity score is calculated using the following formula:
- **Task Completion (40%)**: `completed / (completed + pending)` ratio
- **Goal Progress (30%)**: Progress delta (capped at 30 points)
- **Activity Level (30%)**: Based on conversation count (5 conversations = max score)

### AI Insights Generation
The LLM (Claude 3.5 Sonnet) analyzes:
- Task completion metrics
- Goals worked on
- Conversation activity
- English corrections

And generates:
- Top 3 topics discussed/worked on
- 2-3 key achievements
- 3-4 actionable suggestions
- A friendly 2-3 sentence summary

### Scheduled Job
The `generate_daily_summaries()` job runs at 23:00 every night:
1. Fetches all active users
2. Generates summary for each user
3. Saves to database
4. Logs success/failure for monitoring

### Dashboard UI Features
- Glass-card design matching rest of application
- Lucide-react icons for consistency
- Color scheme: Blue (productivity), Green (tasks), Purple (conversations), Yellow (#F0FF3D - brand color)
- Gradient charts with smooth animations
- Responsive grid layout
- Loading and error states
