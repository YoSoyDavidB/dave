import { useEffect, useState } from 'react'
import {
  BookOpen,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  Clock,
  ChevronRight,
  Loader2,
  RefreshCw,
} from 'lucide-react'
import {
  getRecentCorrections,
  getEnglishStats,
  EnglishCorrection,
  EnglishStats,
} from '../services/api'

const categoryIcons: Record<string, { icon: typeof BookOpen; color: string }> = {
  grammar: { icon: BookOpen, color: 'text-blue-400' },
  vocabulary: { icon: TrendingUp, color: 'text-green-400' },
  spelling: { icon: AlertCircle, color: 'text-orange-400' },
  expression: { icon: CheckCircle2, color: 'text-purple-400' },
}

const categoryLabels: Record<string, string> = {
  grammar: 'Grammar',
  vocabulary: 'Vocabulary',
  spelling: 'Spelling',
  expression: 'Expressions',
}

function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  color,
}: {
  title: string
  value: number | string
  subtitle?: string
  icon: typeof BookOpen
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

function CorrectionCard({ correction }: { correction: EnglishCorrection }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const categoryInfo = categoryIcons[correction.category] || categoryIcons.grammar
  const Icon = categoryInfo.icon

  return (
    <div
      className="glass-card p-4 cursor-pointer transition-all duration-200 hover:border-[#F0FF3D]/20"
      onClick={() => setIsExpanded(!isExpanded)}
    >
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg bg-[var(--bg-input)] ${categoryInfo.color}`}>
          <Icon size={16} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs px-2 py-0.5 rounded-full bg-[var(--bg-input)] text-zinc-400">
              {categoryLabels[correction.category]}
            </span>
            {correction.subcategory && (
              <span className="text-xs text-zinc-500">{correction.subcategory}</span>
            )}
            <span className="text-xs text-zinc-600 ml-auto">
              {new Date(correction.created_at).toLocaleDateString()}
            </span>
          </div>

          <div className="space-y-1">
            <p className="text-red-400/80 text-sm line-through">{correction.original_text}</p>
            <p className="text-[#F0FF3D] text-sm">{correction.corrected_text}</p>
          </div>

          {isExpanded && (
            <div className="mt-3 pt-3 border-t border-[var(--border-color)]">
              <p className="text-zinc-400 text-sm">{correction.explanation}</p>
            </div>
          )}

          <div className="flex items-center gap-1 mt-2 text-zinc-500">
            <ChevronRight
              size={14}
              className={`transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}`}
            />
            <span className="text-xs">{isExpanded ? 'Less' : 'More'}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function CategoryFilter({
  selected,
  onSelect,
  stats,
}: {
  selected: string | null
  onSelect: (category: string | null) => void
  stats: EnglishStats | null
}) {
  const categories = ['grammar', 'vocabulary', 'spelling', 'expression']

  return (
    <div className="flex flex-wrap gap-2">
      <button
        onClick={() => onSelect(null)}
        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
          selected === null
            ? 'bg-[#F0FF3D] text-[#0a0a0f]'
            : 'bg-[var(--bg-input)] text-zinc-400 hover:text-white hover:bg-[var(--bg-input)]/80'
        }`}
      >
        All
      </button>
      {categories.map((cat) => {
        const info = categoryIcons[cat]
        const count = stats?.by_category[cat] || 0
        return (
          <button
            key={cat}
            onClick={() => onSelect(cat)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 flex items-center gap-2 ${
              selected === cat
                ? 'bg-[#F0FF3D] text-[#0a0a0f]'
                : 'bg-[var(--bg-input)] text-zinc-400 hover:text-white hover:bg-[var(--bg-input)]/80'
            }`}
          >
            <info.icon size={14} />
            {categoryLabels[cat]}
            <span className="text-xs opacity-70">({count})</span>
          </button>
        )
      })}
    </div>
  )
}

export default function EnglishProgress() {
  const [stats, setStats] = useState<EnglishStats | null>(null)
  const [corrections, setCorrections] = useState<EnglishCorrection[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [statsData, correctionsData] = await Promise.all([
        getEnglishStats(),
        getRecentCorrections(30, 50),
      ])
      setStats(statsData)
      setCorrections(correctionsData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const filteredCorrections = selectedCategory
    ? corrections.filter((c) => c.category === selectedCategory)
    : corrections

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 size={32} className="animate-spin text-[#F0FF3D]" />
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1">English Progress</h1>
            <p className="text-zinc-500">Track your learning journey with Dave</p>
          </div>
          <button
            onClick={fetchData}
            className="p-2.5 rounded-xl hover:bg-[#F0FF3D]/5 transition-all duration-200 text-zinc-400 hover:text-[#F0FF3D]"
          >
            <RefreshCw size={20} />
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl">
            {error}
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            title="Total Corrections"
            value={stats?.total_corrections || 0}
            subtitle="All time"
            icon={BookOpen}
            color="text-[#F0FF3D]"
          />
          <StatCard
            title="This Week"
            value={stats?.last_7_days || 0}
            subtitle="Last 7 days"
            icon={Clock}
            color="text-[#00d4aa]"
          />
          <StatCard
            title="Most Common"
            value={
              stats?.by_category
                ? Object.entries(stats.by_category).sort((a, b) => b[1] - a[1])[0]?.[0] || '-'
                : '-'
            }
            subtitle="Category to focus on"
            icon={AlertCircle}
            color="text-orange-400"
          />
          <StatCard
            title="Categories"
            value={stats?.by_category ? Object.keys(stats.by_category).length : 0}
            subtitle="Types of errors"
            icon={TrendingUp}
            color="text-purple-400"
          />
        </div>

        {/* Category breakdown */}
        {stats && Object.keys(stats.by_category).length > 0 && (
          <div className="glass-card p-6 mb-8">
            <h2 className="text-lg font-semibold text-white mb-4">Category Breakdown</h2>
            <div className="space-y-3">
              {Object.entries(stats.by_category)
                .sort((a, b) => b[1] - a[1])
                .map(([category, count]) => {
                  const percentage = Math.round((count / stats.total_corrections) * 100)
                  const info = categoryIcons[category] || categoryIcons.grammar
                  return (
                    <div key={category} className="flex items-center gap-3">
                      <div className={`p-1.5 rounded-lg bg-[var(--bg-input)] ${info.color}`}>
                        <info.icon size={14} />
                      </div>
                      <span className="text-zinc-300 text-sm w-24">
                        {categoryLabels[category]}
                      </span>
                      <div className="flex-1 h-2 bg-[var(--bg-input)] rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-[#F0FF3D] to-[#00d4aa] rounded-full transition-all duration-500"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                      <span className="text-zinc-400 text-sm w-16 text-right">
                        {count} ({percentage}%)
                      </span>
                    </div>
                  )
                })}
            </div>
          </div>
        )}

        {/* Corrections List */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Recent Corrections</h2>
          </div>

          <div className="mb-4">
            <CategoryFilter
              selected={selectedCategory}
              onSelect={setSelectedCategory}
              stats={stats}
            />
          </div>

          {filteredCorrections.length === 0 ? (
            <div className="glass-card p-8 text-center">
              <BookOpen size={48} className="mx-auto text-zinc-600 mb-4" />
              <p className="text-zinc-400">No corrections yet</p>
              <p className="text-zinc-600 text-sm mt-1">
                Start chatting with Dave and he'll help you improve your English!
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredCorrections.map((correction) => (
                <CorrectionCard key={correction.id} correction={correction} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
