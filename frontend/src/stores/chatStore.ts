import { create } from 'zustand'
import {
  Message,
  sendMessageStream,
  StreamEvent,
  Source,
  createConversation,
  addMessageToConversation,
  getConversation,
  getConversations,
  deleteConversation as deleteConversationApi,
  ConversationListItem,
} from '../services/api'
import { useAuthStore } from './authStore'

type StreamStatus = 'idle' | 'connecting' | 'streaming' | 'tool_executing'

// Extended message with sources for assistant messages
export interface MessageWithSources extends Message {
  sources?: Source[]
}

interface ChatState {
  // Current conversation
  conversationId: string | null
  messages: MessageWithSources[]
  isLoading: boolean
  streamStatus: StreamStatus
  currentTool: string | null
  error: string | null
  abortController: AbortController | null

  // Conversation list
  conversationGroups: Record<string, ConversationListItem[]>
  isLoadingConversations: boolean

  // Actions
  sendMessage: (content: string) => Promise<void>
  cancelStream: () => void
  clearMessages: () => void
  clearError: () => void
  startNewConversation: () => void
  loadConversation: (id: string) => Promise<void>
  loadConversations: () => Promise<void>
  deleteConversation: (id: string) => Promise<void>
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversationId: null,
  messages: [],
  isLoading: false,
  streamStatus: 'idle',
  currentTool: null,
  error: null,
  abortController: null,
  conversationGroups: {},
  isLoadingConversations: false,

  sendMessage: async (content: string) => {
    const userMessage: Message = { role: 'user', content }
    const abortController = new AbortController()

    // Get or create conversation
    let currentConversationId = get().conversationId

    set((state) => ({
      messages: [...state.messages, userMessage],
      isLoading: true,
      streamStatus: 'connecting',
      currentTool: null,
      error: null,
      abortController,
    }))

    // Create conversation if this is the first message
    if (!currentConversationId) {
      try {
        const newConversation = await createConversation(undefined, [userMessage])
        currentConversationId = newConversation.id
        set({ conversationId: currentConversationId })
      } catch (err) {
        console.error('Failed to create conversation:', err)
        // Continue without persistence
      }
    } else {
      // Save user message to existing conversation
      try {
        await addMessageToConversation(currentConversationId, userMessage)
      } catch (err) {
        console.error('Failed to save user message:', err)
      }
    }

    // Create placeholder for assistant message
    const assistantMessage: Message = { role: 'assistant', content: '' }
    set((state) => ({
      messages: [...state.messages, assistantMessage],
    }))

    const handleStreamEvent = (event: StreamEvent) => {
      switch (event.type) {
        case 'content':
          set((state) => {
            const messages = [...state.messages]
            const lastMessage = messages[messages.length - 1]
            if (lastMessage && lastMessage.role === 'assistant') {
              lastMessage.content += event.content || ''
            }
            return { messages, streamStatus: 'streaming' }
          })
          break

        case 'tool_start':
          set({ streamStatus: 'tool_executing', currentTool: event.tool || null })
          break

        case 'tool_result':
          set({ streamStatus: 'streaming', currentTool: null })
          break

        case 'done': {
          // Update assistant message with sources
          set((state) => {
            const messages = [...state.messages]
            const lastMessage = messages[messages.length - 1]
            if (lastMessage && lastMessage.role === 'assistant' && event.sources) {
              lastMessage.sources = event.sources
            }
            return { messages }
          })

          // Save assistant message to conversation
          const finalMessages = get().messages
          const finalAssistantMessage = finalMessages[finalMessages.length - 1]
          if (currentConversationId && finalAssistantMessage?.role === 'assistant') {
            addMessageToConversation(currentConversationId, {
              role: finalAssistantMessage.role,
              content: finalAssistantMessage.content,
            }).catch(err => {
              console.error('Failed to save assistant message:', err)
            })
          }

          // Refresh conversation list
          get().loadConversations()

          set({
            isLoading: false,
            streamStatus: 'idle',
            currentTool: null,
            abortController: null,
          })
          break
        }

        case 'error':
          set({
            isLoading: false,
            streamStatus: 'idle',
            currentTool: null,
            error: event.error || 'An error occurred',
            abortController: null,
          })
          break
      }
    }

    try {
      // Get user_id from auth store
      const user = useAuthStore.getState().user

      await sendMessageStream(
        {
          messages: get().messages.slice(0, -1),
          user_id: user?.id,
          conversation_id: currentConversationId || undefined,
        },
        handleStreamEvent,
        abortController.signal
      )
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        set({
          isLoading: false,
          streamStatus: 'idle',
          currentTool: null,
          abortController: null,
        })
        return
      }

      set({
        isLoading: false,
        streamStatus: 'idle',
        currentTool: null,
        error: error instanceof Error ? error.message : 'An error occurred',
        abortController: null,
      })
    }
  },

  cancelStream: () => {
    const { abortController } = get()
    if (abortController) {
      abortController.abort()
      set({
        isLoading: false,
        streamStatus: 'idle',
        currentTool: null,
        abortController: null,
      })
    }
  },

  clearMessages: () => set({
    messages: [],
    error: null,
    streamStatus: 'idle',
    currentTool: null,
    conversationId: null,
  }),

  clearError: () => set({ error: null }),

  startNewConversation: () => {
    set({
      conversationId: null,
      messages: [],
      error: null,
      streamStatus: 'idle',
      currentTool: null,
    })
  },

  loadConversation: async (id: string) => {
    try {
      set({ isLoading: true, error: null })
      const conversation = await getConversation(id)
      set({
        conversationId: conversation.id,
        messages: conversation.messages.map(m => ({
          role: m.role as 'user' | 'assistant',
          content: m.content,
        })),
        isLoading: false,
      })
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to load conversation',
      })
    }
  },

  loadConversations: async () => {
    try {
      set({ isLoadingConversations: true })
      const data = await getConversations()
      set({
        conversationGroups: data.groups,
        isLoadingConversations: false,
      })
    } catch (error) {
      console.error('Failed to load conversations:', error)
      set({ isLoadingConversations: false })
    }
  },

  deleteConversation: async (id: string) => {
    try {
      await deleteConversationApi(id)

      // If we deleted the current conversation, clear it
      if (get().conversationId === id) {
        get().startNewConversation()
      }

      // Refresh the list
      await get().loadConversations()
    } catch (error) {
      console.error('Failed to delete conversation:', error)
    }
  },
}))
