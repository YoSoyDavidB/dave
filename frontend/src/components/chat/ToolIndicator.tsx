import {
  Wrench,
  FileText,
  FolderOpen,
  Search,
  Calendar,
  Plus,
  BookOpen,
  TrendingUp,
  Loader2,
  CheckCircle2,
} from 'lucide-react'

interface ToolInfo {
  icon: typeof Wrench
  label: string
  description: string
  color: string
}

const toolInfoMap: Record<string, ToolInfo> = {
  // Vault tools
  read_note: {
    icon: FileText,
    label: 'Reading note',
    description: 'Fetching note from your vault',
    color: 'text-blue-400',
  },
  read_daily_note: {
    icon: Calendar,
    label: 'Reading daily note',
    description: "Getting today's daily note",
    color: 'text-[#F0FF3D]',
  },
  create_note: {
    icon: Plus,
    label: 'Creating note',
    description: 'Creating a new note in your vault',
    color: 'text-green-400',
  },
  list_directory: {
    icon: FolderOpen,
    label: 'Browsing vault',
    description: 'Listing files in directory',
    color: 'text-purple-400',
  },
  search_vault: {
    icon: Search,
    label: 'Searching vault',
    description: 'Finding relevant notes',
    color: 'text-cyan-400',
  },
  append_to_daily_note: {
    icon: Calendar,
    label: 'Updating daily note',
    description: 'Adding content to your daily note',
    color: 'text-[#F0FF3D]',
  },
  create_daily_note: {
    icon: Calendar,
    label: 'Creating daily note',
    description: "Creating today's daily note",
    color: 'text-green-400',
  },
  // English tools
  log_english_correction: {
    icon: BookOpen,
    label: 'Logging correction',
    description: 'Saving your learning progress',
    color: 'text-orange-400',
  },
  get_english_progress: {
    icon: TrendingUp,
    label: 'Checking progress',
    description: 'Getting your learning stats',
    color: 'text-green-400',
  },
  get_recent_english_errors: {
    icon: BookOpen,
    label: 'Reviewing errors',
    description: 'Getting recent corrections',
    color: 'text-orange-400',
  },
}

const defaultToolInfo: ToolInfo = {
  icon: Wrench,
  label: 'Processing',
  description: 'Running tool',
  color: 'text-zinc-400',
}

interface ToolIndicatorProps {
  toolName: string | null
  status: 'executing' | 'completed'
}

export default function ToolIndicator({ toolName, status }: ToolIndicatorProps) {
  if (!toolName) return null

  const info = toolInfoMap[toolName] || {
    ...defaultToolInfo,
    label: toolName.replace(/_/g, ' '),
  }
  const Icon = info.icon

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)] ${
        status === 'completed' ? 'opacity-60' : ''
      }`}
    >
      {status === 'executing' ? (
        <Loader2 size={14} className={`animate-spin ${info.color}`} />
      ) : (
        <CheckCircle2 size={14} className="text-green-400" />
      )}
      <Icon size={14} className={info.color} />
      <span className="text-sm text-zinc-300">{info.label}</span>
    </div>
  )
}

// Compact version for inline use
export function ToolIndicatorCompact({
  toolName,
  isExecuting,
}: {
  toolName: string
  isExecuting: boolean
}) {
  const info = toolInfoMap[toolName] || defaultToolInfo
  const Icon = info.icon

  return (
    <div className="flex items-center gap-2 text-sm">
      {isExecuting ? (
        <Loader2 size={14} className={`animate-spin ${info.color}`} />
      ) : (
        <Icon size={14} className={info.color} />
      )}
      <span className={info.color}>{info.label}...</span>
    </div>
  )
}

// Used tools badge for message footer
export function UsedToolsBadge({ tools }: { tools: string[] }) {
  if (tools.length === 0) return null

  return (
    <div className="flex flex-wrap gap-1.5 mt-2 pt-2 border-t border-[var(--border-color)]">
      <span className="text-xs text-zinc-600">Used:</span>
      {tools.map((tool) => {
        const info = toolInfoMap[tool] || defaultToolInfo
        const Icon = info.icon
        return (
          <span
            key={tool}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[var(--bg-input)] text-xs text-zinc-400"
          >
            <Icon size={10} />
            {info.label}
          </span>
        )
      })}
    </div>
  )
}
