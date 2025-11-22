import { create } from 'zustand'
import { Message, sendMessage } from '../services/api'

interface ChatState {
  messages: Message[]
  isLoading: boolean
  error: string | null
  sendMessage: (content: string) => Promise<void>
  clearMessages: () => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  error: null,

  sendMessage: async (content: string) => {
    const userMessage: Message = { role: 'user', content }

    set((state) => ({
      messages: [...state.messages, userMessage],
      isLoading: true,
      error: null,
    }))

    try {
      const response = await sendMessage({
        messages: [...get().messages],
      })

      set((state) => ({
        messages: [...state.messages, response.message],
        isLoading: false,
      }))
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'An error occurred',
      })
    }
  },

  clearMessages: () => set({ messages: [], error: null }),
}))
