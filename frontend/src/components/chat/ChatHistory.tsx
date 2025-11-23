import { Plus, MessageSquare, Search } from 'lucide-react'

interface ChatHistoryProps {
  onNewChat: () => void
}

export default function ChatHistory({ onNewChat }: ChatHistoryProps) {
  // Mock data - in the future this will come from a store
  const historyGroups = [
    {
      label: 'Today',
      items: [
        { id: '1', title: 'Help me practice English conversation...', date: 'today' },
        { id: '2', title: 'Create a daily note for my meeting...', date: 'today' },
        { id: '3', title: 'Review my weekly goals and tasks...', date: 'today' },
        { id: '4', title: 'Grammar tips for present perfect...', date: 'today' },
        { id: '5', title: 'Organize notes about the project...', date: 'today' },
      ],
    },
    {
      label: '5 Days Ago',
      items: [
        { id: '6', title: 'Schedule reminder for dentist...', date: '5 days ago' },
        { id: '7', title: 'Ideas for productivity system...', date: '5 days ago' },
        { id: '8', title: 'English tips for writing emails...', date: '5 days ago' },
      ],
    },
    {
      label: '7 Days Ago',
      items: [
        { id: '9', title: 'Weekly review and planning...', date: '7 days ago' },
      ],
    },
  ]

  return (
    <div className="w-80 h-full glass flex flex-col border-l border-white/[0.06]">
      {/* Header */}
      <div className="p-4 flex items-center justify-between border-b border-white/[0.06]">
        <h2 className="text-white font-semibold">Chat History</h2>
        <button
          onClick={onNewChat}
          className="flex items-center gap-2 px-3 py-1.5 btn-gradient text-sm font-medium rounded-lg"
        >
          <Plus size={16} />
          New Chat
        </button>
      </div>

      {/* Search */}
      <div className="px-4 py-3">
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
          <input
            type="text"
            placeholder="Search conversations..."
            className="w-full bg-[rgba(14,14,20,0.6)] border border-white/[0.06] rounded-xl py-2.5 pl-10 pr-4 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-[#F0FF3D]/40 focus:shadow-[0_0_0_3px_rgba(240,255,61,0.08)] transition-all"
          />
        </div>
      </div>

      {/* History list */}
      <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-5">
        {historyGroups.map((group) => (
          <div key={group.label}>
            <h3 className="text-xs text-zinc-600 font-medium mb-2 px-2 uppercase tracking-wider">
              {group.label}
            </h3>
            <div className="space-y-1">
              {group.items.map((item) => (
                <div key={item.id} className="history-item group">
                  <div className="w-9 h-9 rounded-xl bg-[rgba(20,20,32,0.8)] border border-white/[0.06] flex items-center justify-center flex-shrink-0 group-hover:border-[#F0FF3D]/30 group-hover:bg-[#F0FF3D]/5 transition-all">
                    <MessageSquare size={14} className="text-zinc-500 group-hover:text-[#F0FF3D] transition-colors" />
                  </div>
                  <span className="text-sm text-zinc-400 truncate group-hover:text-white transition-colors">
                    {item.title}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-white/[0.06]">
        <div className="flex items-center justify-between text-xs text-zinc-600">
          <span>9 conversations</span>
          <button className="text-[#F0FF3D]/70 hover:text-[#F0FF3D] transition-colors">
            Clear all
          </button>
        </div>
      </div>
    </div>
  )
}
