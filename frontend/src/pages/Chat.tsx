import { useState, useRef, useEffect, FormEvent } from 'react'
import { Send, Sparkles, Search, MoreVertical, Square, Loader2 } from 'lucide-react'
import { useChatStore } from '../stores/chatStore'
import ChatHistory from '../components/chat/ChatHistory'
import MarkdownMessage from '../components/chat/MarkdownMessage'
import { ToolIndicatorCompact } from '../components/chat/ToolIndicator'

// Futuristic smoke orb avatar component
function SmokeOrb({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'w-9 h-9',
    md: 'w-10 h-10',
    lg: 'w-28 h-28'
  }

  if (size === 'lg') {
    return (
      <div className={`${sizeClasses[size]} avatar-orb-large relative`}>
        {/* Smoke particles */}
        <div className="smoke-particle smoke-particle-1" />
        <div className="smoke-particle smoke-particle-2" />
        <div className="smoke-particle smoke-particle-3" />
        {/* Inner ring */}
        <div className="avatar-inner-ring" />
        {/* Core glow */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-8 h-8 rounded-full bg-[#F0FF3D]/30 blur-md animate-pulse" />
        </div>
      </div>
    )
  }

  return (
    <div className={`${sizeClasses[size]} rounded-xl overflow-hidden relative`}>
      <div className="avatar-orb w-full h-full">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-3 h-3 rounded-full bg-[#F0FF3D]/50 blur-sm" />
        </div>
      </div>
    </div>
  )
}

// Streaming indicator component
function StreamingIndicator({ status, tool }: { status: string; tool: string | null }) {
  if (status === 'connecting') {
    return (
      <div className="flex items-center gap-2 text-zinc-500 text-sm">
        <Loader2 size={14} className="animate-spin" />
        <span>Connecting...</span>
      </div>
    )
  }

  if (status === 'tool_executing' && tool) {
    return <ToolIndicatorCompact toolName={tool} isExecuting={true} />
  }

  if (status === 'streaming') {
    return (
      <div className="flex items-center gap-2 text-[#F0FF3D]/70 text-sm">
        <div className="flex space-x-1">
          <div className="w-1.5 h-1.5 bg-[#F0FF3D] rounded-full animate-pulse" />
          <div className="w-1.5 h-1.5 bg-[#F0FF3D] rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
          <div className="w-1.5 h-1.5 bg-[#F0FF3D] rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
        </div>
        <span>Typing...</span>
      </div>
    )
  }

  return null
}

export default function Chat() {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const {
    messages,
    isLoading,
    streamStatus,
    currentTool,
    error,
    sendMessage,
    cancelStream,
    startNewConversation,
    clearError
  } = useChatStore()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const message = input.trim()
    setInput('')
    await sendMessage(message)
  }

  const handleNewChat = () => {
    startNewConversation()
  }

  const handleCancel = () => {
    cancelStream()
  }

  // Check if the last assistant message is empty (still streaming)
  const lastMessage = messages[messages.length - 1]
  const isStreamingEmpty = isLoading && lastMessage?.role === 'assistant' && !lastMessage.content

  return (
    <div className="flex h-full">
      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Chat header */}
        <div className="flex items-center justify-between px-6 py-3 border-b border-white/[0.06]">
          <div className="flex items-center gap-3">
            <div className="glow-soft rounded-xl">
              <SmokeOrb size="md" />
            </div>
            <div>
              <h2 className="text-white font-medium flex items-center gap-2">
                Dave
                <span className={`w-2 h-2 rounded-full ${isLoading ? 'bg-[#F0FF3D] animate-pulse' : 'notification-dot'}`}></span>
              </h2>
              <span className="text-xs text-zinc-500">
                {isLoading ? (
                  <StreamingIndicator status={streamStatus} tool={currentTool} />
                ) : (
                  'Always ready to help'
                )}
              </span>
            </div>
          </div>
          <button className="p-2.5 rounded-xl hover:bg-[#F0FF3D]/5 transition-all duration-200 text-zinc-500 hover:text-[#F0FF3D]">
            <MoreVertical size={20} />
          </button>
        </div>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-6 py-8">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center min-h-[400px]">
                {/* Large animated smoke orb avatar */}
                <div className="relative mb-8 animate-float">
                  <div className="glow-primary rounded-full">
                    <SmokeOrb size="lg" />
                  </div>
                  {/* Orbiting elements */}
                  <div className="absolute -inset-4 rounded-full border border-[#F0FF3D]/20 animate-pulse" style={{ animationDuration: '3s' }}></div>
                  <div className="absolute -inset-8 rounded-full border border-[#00d4aa]/10"></div>
                </div>

                {/* Welcome text */}
                <h1 className="text-3xl font-semibold text-white mb-3 text-center">
                  Hey there! What can<br />I help you with?
                </h1>
                <p className="text-zinc-500 text-center max-w-md">
                  I'm Dave, your AI friend for productivity and learning English.
                </p>

                {/* Quick action buttons with glow border effect */}
                <div className="flex gap-3 mt-8">
                  <button className="px-4 py-2.5 rounded-xl btn-glow-border text-sm">
                    <Sparkles size={14} className="inline mr-2" />
                    Generate ideas
                  </button>
                  <button className="px-4 py-2.5 rounded-xl btn-glow-border text-sm">
                    <Search size={14} className="inline mr-2" />
                    Research topic
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {messages.map((message, index) => {
                  // Skip empty assistant messages that are still being streamed
                  if (message.role === 'assistant' && !message.content && index === messages.length - 1 && isLoading) {
                    return null
                  }

                  return (
                    <div
                      key={index}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className="flex items-start gap-3 max-w-[80%]">
                        {message.role === 'assistant' && (
                          <div className="flex-shrink-0">
                            <SmokeOrb size="sm" />
                          </div>
                        )}
                        <div
                          className={`px-4 py-3 rounded-2xl ${
                            message.role === 'user'
                              ? 'message-user rounded-br-md'
                              : 'message-assistant rounded-bl-md'
                          }`}
                        >
                          {message.role === 'assistant' ? (
                            <MarkdownMessage
                              content={message.content}
                              isStreaming={index === messages.length - 1 && isLoading && streamStatus === 'streaming'}
                            />
                          ) : (
                            <p className="text-sm leading-relaxed whitespace-pre-wrap">
                              {message.content}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}

                {/* Show typing indicator when connecting or waiting for content */}
                {isLoading && (isStreamingEmpty || streamStatus === 'connecting' || streamStatus === 'tool_executing') && (
                  <div className="flex justify-start">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0">
                        <SmokeOrb size="sm" />
                      </div>
                      <div className="message-assistant px-4 py-3 rounded-2xl rounded-bl-md">
                        {streamStatus === 'tool_executing' && currentTool ? (
                          <ToolIndicatorCompact toolName={currentTool} isExecuting={true} />
                        ) : (
                          <div className="flex space-x-1.5">
                            <div className="w-2 h-2 bg-[#F0FF3D] rounded-full animate-bounce" />
                            <div className="w-2 h-2 bg-[#F0FF3D] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                            <div className="w-2 h-2 bg-[#F0FF3D] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            )}

            {/* Error message */}
            {error && (
              <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-sm flex items-center justify-between">
                <span>{error}</span>
                <button
                  onClick={clearError}
                  className="text-red-400 hover:text-red-300 transition-colors"
                >
                  Dismiss
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Input area */}
        <div className="p-6">
          <div className="max-w-3xl mx-auto">
            <form onSubmit={handleSubmit}>
              <div className="chat-input rounded-2xl p-2">
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Start your request, and let Dave handle everything..."
                    disabled={isLoading}
                    className="flex-1 bg-transparent px-4 py-2.5 text-white placeholder-zinc-500 focus:outline-none disabled:opacity-50"
                  />
                  {isLoading ? (
                    <button
                      type="button"
                      onClick={handleCancel}
                      className="p-3 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-xl transition-all duration-200"
                      title="Cancel"
                    >
                      <Square size={18} />
                    </button>
                  ) : (
                    <button
                      type="submit"
                      disabled={!input.trim()}
                      className="p-3 btn-gradient rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none"
                    >
                      <Send size={18} />
                    </button>
                  )}
                </div>

                {/* Options row */}
                <div className="flex items-center gap-4 px-4 py-2.5 mt-1 border-t border-white/[0.06]">
                  <button
                    type="button"
                    className="flex items-center gap-2 text-sm text-zinc-500 hover:text-[#F0FF3D] transition-colors"
                  >
                    <Sparkles size={16} />
                    Reasoning
                  </button>
                  <button
                    type="button"
                    className="flex items-center gap-2 text-sm text-zinc-500 hover:text-[#F0FF3D] transition-colors"
                  >
                    <Search size={16} />
                    Deep Research
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>

      {/* History sidebar */}
      <ChatHistory onNewChat={handleNewChat} />
    </div>
  )
}
