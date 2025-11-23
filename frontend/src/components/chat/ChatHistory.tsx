import { useEffect } from 'react'
import { Plus, MessageSquare, Search, Trash2 } from 'lucide-react'
import { useChatStore } from '../../stores/chatStore'

interface ChatHistoryProps {
  onNewChat: () => void
}

export default function ChatHistory({ onNewChat }: ChatHistoryProps) {
  const {
    conversationId,
    conversationGroups,
    isLoadingConversations,
    loadConversations,
    loadConversation,
    deleteConversation,
  } = useChatStore()

  // Load conversations on mount
  useEffect(() => {
    loadConversations()
  }, [loadConversations])

  // Calculate total conversations
  const totalConversations = Object.values(conversationGroups).reduce(
    (acc, group) => acc + group.length,
    0
  )

  // Convert groups object to array for rendering
  const groupOrder = ['Today', 'Yesterday', 'This Week', 'Older']
  const historyGroups = groupOrder
    .filter((label) => conversationGroups[label]?.length > 0)
    .map((label) => ({
      label,
      items: conversationGroups[label],
    }))

  const handleConversationClick = async (id: string) => {
    if (id !== conversationId) {
      await loadConversation(id)
    }
  }

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    await deleteConversation(id)
  }

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
        {isLoadingConversations ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-pulse text-zinc-500 text-sm">Loading...</div>
          </div>
        ) : historyGroups.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-zinc-500">
            <MessageSquare size={32} className="mb-2 opacity-50" />
            <p className="text-sm">No conversations yet</p>
            <p className="text-xs mt-1">Start a new chat to begin</p>
          </div>
        ) : (
          historyGroups.map((group) => (
            <div key={group.label}>
              <h3 className="text-xs text-zinc-600 font-medium mb-2 px-2 uppercase tracking-wider">
                {group.label}
              </h3>
              <div className="space-y-1">
                {group.items.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => handleConversationClick(item.id)}
                    className={`history-item group cursor-pointer ${
                      item.id === conversationId ? 'bg-[#F0FF3D]/10 border-[#F0FF3D]/30' : ''
                    }`}
                  >
                    <div
                      className={`w-9 h-9 rounded-xl border flex items-center justify-center flex-shrink-0 transition-all ${
                        item.id === conversationId
                          ? 'bg-[#F0FF3D]/10 border-[#F0FF3D]/30'
                          : 'bg-[rgba(20,20,32,0.8)] border-white/[0.06] group-hover:border-[#F0FF3D]/30 group-hover:bg-[#F0FF3D]/5'
                      }`}
                    >
                      <MessageSquare
                        size={14}
                        className={`transition-colors ${
                          item.id === conversationId
                            ? 'text-[#F0FF3D]'
                            : 'text-zinc-500 group-hover:text-[#F0FF3D]'
                        }`}
                      />
                    </div>
                    <span
                      className={`text-sm truncate flex-1 transition-colors ${
                        item.id === conversationId
                          ? 'text-white'
                          : 'text-zinc-400 group-hover:text-white'
                      }`}
                    >
                      {item.title}
                    </span>
                    <button
                      onClick={(e) => handleDelete(e, item.id)}
                      className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg hover:bg-red-500/20 text-zinc-500 hover:text-red-400 transition-all"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-white/[0.06]">
        <div className="flex items-center justify-between text-xs text-zinc-600">
          <span>{totalConversations} conversation{totalConversations !== 1 ? 's' : ''}</span>
        </div>
      </div>
    </div>
  )
}
