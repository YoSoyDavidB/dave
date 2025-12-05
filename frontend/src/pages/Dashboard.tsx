import { useEffect, useState } from 'react'
import {
  TrendingUp,
  CheckCircle2,
  MessageSquare,
  Target,
  Calendar,
  Sparkles,
  Lightbulb,
  Trophy,
  RefreshCw,
  Loader2,
  AlertCircle,
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { getDashboardStats, generateDailySummary, type DashboardStats, type DailySummary } from '../services/api'
import FocusTimer from '../components/focus/FocusTimer'

export default function Dashboard() {
  const { user } = useAuthStore()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    loadDashboard()
  }, [user])

  const loadDashboard = async () => {
    if (!user) return

    try {
      setLoading(true)
      setError(null)
      const data = await getDashboardStats(user.id)
      setStats(data)
    } catch (err) {
      console.error('Failed to load dashboard:', err)
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateSummary = async () => {
    if (!user) return

    try {
      setGenerating(true)
      await generateDailySummary(user.id)
      // Reload dashboard after generating
      await loadDashboard()
    } catch (err) {
      console.error('Failed to generate summary:', err)
      setError('Failed to generate summary')
    } finally {
      setGenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="flex items-center gap-3 text-zinc-400">
          <Loader2 className="animate-spin" size={24} />
          <span>Loading dashboard...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="glass-card p-6 border-red-500/20">
          <div className="flex items-start gap-3">
            <AlertCircle className="text-red-400" size={24} />
            <div className="flex-1">
              <p className="text-red-400 font-medium mb-2">{error}</p>
              <button
                onClick={loadDashboard}
                className="text-sm text-zinc-400 hover:text-[#F0FF3D] underline transition-colors"
              >
                Try again
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const todaySummary = stats?.today_summary

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Dashboard</h1>
          <p className="text-zinc-400 text-sm">Track your productivity and progress</p>
        </div>
        <button
          onClick={handleGenerateSummary}
          disabled={generating}
          className="btn-primary flex items-center gap-2"
        >
          {generating ? (
            <>
              <Loader2 className="animate-spin" size={18} />
              Generating...
            </>
          ) : (
            <>
              <RefreshCw size={18} />
              Generate Summary
            </>
          )}
        </button>
      </div>

      {/* Today's Summary Card */}
      {todaySummary ? (
        <DailySummaryCard summary={todaySummary} />
      ) : (
        <div className="glass-card p-6 border-yellow-500/20">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-[var(--bg-input)] text-yellow-400">
              <Calendar size={24} />
            </div>
            <div className="flex-1">
              <h3 className="text-white font-semibold mb-2">No summary yet for today</h3>
              <p className="text-zinc-400 mb-4">
                Generate your daily summary to see insights, achievements, and suggestions.
              </p>
              <button
                onClick={handleGenerateSummary}
                disabled={generating}
                className="btn-secondary flex items-center gap-2"
              >
                {generating ? (
                  <>
                    <Loader2 className="animate-spin" size={18} />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles size={18} />
                    Generate Summary
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="Week Productivity"
          value={`${stats?.week_productivity_avg.toFixed(1) || 0}/100`}
          icon={TrendingUp}
          color="text-blue-400"
        />
        <StatCard
          title="Tasks Completed"
          value={stats?.week_tasks_completed || 0}
          subtitle="this week"
          icon={CheckCircle2}
          color="text-green-400"
        />
        <StatCard
          title="Conversations"
          value={stats?.week_conversations || 0}
          subtitle="this week"
          icon={MessageSquare}
          color="text-purple-400"
        />
        <StatCard
          title="Today's Score"
          value={todaySummary?.productivity_score.toFixed(1) || '—'}
          icon={Target}
          color="text-[#F0FF3D]"
        />
      </div>

      {/* Focus Mode Timer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <FocusTimer />
        </div>

        {/* Quick Stats Section */}
        <div className="lg:col-span-2 space-y-4">
          {todaySummary && todaySummary.key_achievements.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Trophy size={20} className="text-yellow-400" />
                Today's Achievements
              </h3>
              <ul className="space-y-2">
                {todaySummary.key_achievements.slice(0, 3).map((achievement, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-zinc-300">
                    <CheckCircle2 size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
                    <span>{achievement}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {todaySummary && todaySummary.suggestions.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Lightbulb size={20} className="text-[#F0FF3D]" />
                Suggestions for Today
              </h3>
              <ul className="space-y-2">
                {todaySummary.suggestions.slice(0, 3).map((suggestion, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-zinc-300">
                    <span className="text-[#F0FF3D] mt-0.5 flex-shrink-0">→</span>
                    <span>{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Productivity Trend */}
      {stats && stats.productivity_trend.length > 0 && (
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <TrendingUp size={20} className="text-blue-400" />
            Productivity Trend
          </h2>
          <ProductivityChart data={stats.productivity_trend} />
        </div>
      )}

      {/* Tasks Trend */}
      {stats && stats.tasks_trend.length > 0 && (
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <CheckCircle2 size={20} className="text-green-400" />
            Tasks Overview
          </h2>
          <TasksChart data={stats.tasks_trend} />
        </div>
      )}
    </div>
  )
}

// Daily Summary Card Component
function DailySummaryCard({ summary }: { summary: DailySummary }) {
  return (
    <div className="glass-card p-6 border-[#F0FF3D]/20">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Sparkles size={24} className="text-[#F0FF3D]" />
          Today's Summary
        </h2>
        <div className="text-right">
          <div className="text-3xl font-bold text-[#F0FF3D]">{summary.productivity_score}</div>
          <div className="text-sm text-zinc-400">Productivity Score</div>
        </div>
      </div>

      {/* Summary Text */}
      {summary.summary_text && (
        <div className="bg-[var(--bg-input)] rounded-xl p-4 mb-6">
          <p className="text-zinc-300">{summary.summary_text}</p>
        </div>
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <MetricItem label="Tasks Done" value={summary.tasks_completed} color="text-green-400" />
        <MetricItem label="Tasks Created" value={summary.tasks_created} color="text-blue-400" />
        <MetricItem label="Conversations" value={summary.conversations_count} color="text-purple-400" />
        <MetricItem label="English Fixes" value={summary.english_corrections} color="text-orange-400" />
      </div>

      {/* Key Achievements */}
      {summary.key_achievements.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <Trophy size={16} className="text-yellow-400" />
            Key Achievements
          </h3>
          <ul className="space-y-2">
            {summary.key_achievements.map((achievement, idx) => (
              <li key={idx} className="flex items-start gap-2 text-zinc-300">
                <CheckCircle2 size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
                <span>{achievement}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Top Topics */}
      {summary.top_topics.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <Sparkles size={16} className="text-[#F0FF3D]" />
            Top Topics
          </h3>
          <div className="flex flex-wrap gap-2">
            {summary.top_topics.map((topic, idx) => (
              <span
                key={idx}
                className="px-3 py-1.5 bg-[var(--bg-input)] text-zinc-300 rounded-full text-sm border border-[var(--border-color)]"
              >
                {topic}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Suggestions */}
      {summary.suggestions.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <Lightbulb size={16} className="text-[#F0FF3D]" />
            Suggestions
          </h3>
          <ul className="space-y-2">
            {summary.suggestions.map((suggestion, idx) => (
              <li key={idx} className="flex items-start gap-2 text-zinc-300">
                <span className="text-[#F0FF3D] mt-0.5 flex-shrink-0">→</span>
                <span>{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Goals Updated */}
      {summary.goals_updated.length > 0 && (
        <div className="pt-6 border-t border-[var(--border-color)]">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <Target size={16} className="text-blue-400" />
            Goals Worked On
          </h3>
          <ul className="space-y-2">
            {summary.goals_updated.map((goal, idx) => (
              <li key={idx} className="text-zinc-300 flex items-start gap-2">
                <span className="text-zinc-500 flex-shrink-0">•</span>
                <span>{goal}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

// Stat Card Component
function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  color,
}: {
  title: string
  value: string | number
  subtitle?: string
  icon: typeof TrendingUp
  color: string
}) {
  return (
    <div className="glass-card p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-zinc-400 text-sm mb-1">{title}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
          {subtitle && <p className="text-zinc-500 text-xs mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-xl bg-[var(--bg-input)] ${color}`}>
          <Icon size={24} />
        </div>
      </div>
    </div>
  )
}

// Metric Item Component
function MetricItem({
  label,
  value,
  color,
}: {
  label: string
  value: number
  color: string
}) {
  return (
    <div className="text-center bg-[var(--bg-input)] rounded-xl p-4">
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
      <div className="text-xs text-zinc-400 mt-1">{label}</div>
    </div>
  )
}

// Simple Productivity Chart (using bars)
function ProductivityChart({ data }: { data: Array<{ date: string; score: number }> }) {
  const maxScore = Math.max(...data.map((d) => d.score), 100)

  return (
    <div className="space-y-3">
      {data.map((item, idx) => {
        const date = new Date(item.date)
        const dayName = date.toLocaleDateString('en-US', { weekday: 'short' })
        const percentage = (item.score / maxScore) * 100

        return (
          <div key={idx} className="flex items-center gap-3">
            <div className="w-12 text-sm text-zinc-400">{dayName}</div>
            <div className="flex-1 bg-[var(--bg-input)] rounded-full h-8 relative overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-500 to-[#F0FF3D] h-8 rounded-full transition-all duration-500"
                style={{ width: `${percentage}%` }}
              />
              <div className="absolute inset-0 flex items-center justify-end pr-3">
                <span className="text-xs font-semibold text-white drop-shadow-lg">{item.score.toFixed(1)}</span>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

// Simple Tasks Chart (using bars)
function TasksChart({ data }: { data: Array<{ date: string; completed: number; created: number }> }) {
  const maxTasks = Math.max(...data.flatMap((d) => [d.completed, d.created]), 10)

  return (
    <div className="space-y-4">
      {data.map((item, idx) => {
        const date = new Date(item.date)
        const dayName = date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
        const completedPercentage = (item.completed / maxTasks) * 100
        const createdPercentage = (item.created / maxTasks) * 100

        return (
          <div key={idx}>
            <div className="text-sm text-zinc-400 mb-2">{dayName}</div>
            <div className="flex gap-4">
              <div className="flex-1">
                <div className="text-xs text-green-400 mb-1.5 flex items-center gap-1">
                  <CheckCircle2 size={12} />
                  Completed: {item.completed}
                </div>
                <div className="bg-[var(--bg-input)] rounded-full h-6 overflow-hidden">
                  <div
                    className="bg-green-500 h-6 rounded-full transition-all duration-500"
                    style={{ width: `${completedPercentage}%` }}
                  />
                </div>
              </div>
              <div className="flex-1">
                <div className="text-xs text-blue-400 mb-1.5 flex items-center gap-1">
                  <Target size={12} />
                  Created: {item.created}
                </div>
                <div className="bg-[var(--bg-input)] rounded-full h-6 overflow-hidden">
                  <div
                    className="bg-blue-500 h-6 rounded-full transition-all duration-500"
                    style={{ width: `${createdPercentage}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
