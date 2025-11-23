const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export interface Message {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatRequest {
  messages: Message[]
  model?: string
}

export interface ChatResponse {
  message: Message
  model: string
  usage?: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
  tools_used?: string[]
}

// Stream event types from the backend
export type StreamEventType = 'content' | 'tool_start' | 'tool_result' | 'done' | 'error'

export interface StreamEvent {
  type: StreamEventType
  content?: string
  tool?: string
  success?: boolean
  tools_used?: string[] | null
  error?: string
}

export type StreamCallback = (event: StreamEvent) => void

/**
 * Send a message and get a non-streaming response
 */
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || 'Failed to send message')
  }

  return response.json()
}

/**
 * Send a message and get a streaming response via SSE
 */
export async function sendMessageStream(
  request: ChatRequest,
  onEvent: StreamCallback,
  signal?: AbortSignal
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
    signal,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || 'Failed to send message')
  }

  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('No response body')
  }

  const decoder = new TextDecoder()
  let buffer = ''

  try {
    // eslint-disable-next-line no-constant-condition
    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        break
      }

      buffer += decoder.decode(value, { stream: true })

      // Process complete SSE events (lines ending with \n\n)
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || '' // Keep incomplete data in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6) // Remove "data: " prefix

          try {
            const event: StreamEvent = JSON.parse(data)
            onEvent(event)

            // Stop processing if we received done or error
            if (event.type === 'done' || event.type === 'error') {
              return
            }
          } catch {
            console.warn('Failed to parse SSE event:', data)
          }
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}

/**
 * Health check endpoint
 */
export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/health`)
  return response.json()
}

// ============================================
// CONVERSATION API
// ============================================

export interface ConversationListItem {
  id: string
  title: string
  updated_at: string
}

export interface GroupedConversations {
  groups: Record<string, ConversationListItem[]>
}

export interface ConversationDetail {
  id: string
  title: string | null
  created_at: string
  updated_at: string
  messages: Message[]
}

/**
 * Get all conversations grouped by time period
 */
export async function getConversations(): Promise<GroupedConversations> {
  const response = await fetch(`${API_BASE_URL}/conversations`)
  if (!response.ok) {
    throw new Error('Failed to fetch conversations')
  }
  return response.json()
}

/**
 * Get a single conversation with all messages
 */
export async function getConversation(id: string): Promise<ConversationDetail> {
  const response = await fetch(`${API_BASE_URL}/conversations/${id}`)
  if (!response.ok) {
    throw new Error('Failed to fetch conversation')
  }
  return response.json()
}

/**
 * Create a new conversation
 */
export async function createConversation(
  title?: string,
  messages?: Message[]
): Promise<ConversationDetail> {
  const response = await fetch(`${API_BASE_URL}/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, messages }),
  })
  if (!response.ok) {
    throw new Error('Failed to create conversation')
  }
  return response.json()
}

/**
 * Add a message to a conversation
 */
export async function addMessageToConversation(
  conversationId: string,
  message: Message
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(message),
  })
  if (!response.ok) {
    throw new Error('Failed to add message')
  }
}

/**
 * Delete a conversation
 */
export async function deleteConversation(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/conversations/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error('Failed to delete conversation')
  }
}
