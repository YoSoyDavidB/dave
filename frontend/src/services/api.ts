const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const defaultFetchOptions: RequestInit = {
  credentials: 'include', // Send cookies with every request
}

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
    ...defaultFetchOptions,
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
    ...defaultFetchOptions,
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
  const response = await fetch(`${API_BASE_URL}/health`, defaultFetchOptions)
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
  const response = await fetch(`${API_BASE_URL}/conversations`, defaultFetchOptions)
  if (!response.ok) {
    throw new Error('Failed to fetch conversations')
  }
  return response.json()
}

/**
 * Get a single conversation with all messages
 */
export async function getConversation(id: string): Promise<ConversationDetail> {
  const response = await fetch(`${API_BASE_URL}/conversations/${id}`, defaultFetchOptions)
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
    ...defaultFetchOptions,
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
    ...defaultFetchOptions,
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
    ...defaultFetchOptions,
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error('Failed to delete conversation')
  }
}

// ============================================
// AUTH API
// ============================================

export interface LoginCredentials {
  email: string
  password: string
}

export type RegisterCredentials = LoginCredentials

export interface User {
  id: string
  email: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export async function login(credentials: LoginCredentials): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    ...defaultFetchOptions,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || 'Login failed')
  }
  
  // After successful login, the cookie is set. We can then get the user data.
  return getMe()
}

export async function register(credentials: RegisterCredentials): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    ...defaultFetchOptions,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || 'Registration failed')
  }
}

export async function logout(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/auth/logout`, {
    ...defaultFetchOptions,
    method: 'POST',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || 'Logout failed')
  }
}

export async function getMe(): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, defaultFetchOptions)
  if (!response.ok) {
    throw new Error('Not authenticated')
  }
  return response.json()
}

// ============================================
// ENGLISH CORRECTIONS API
// ============================================

export interface EnglishCorrection {
  id: number
  created_at: string
  original_text: string
  corrected_text: string
  explanation: string
  category: 'grammar' | 'vocabulary' | 'spelling' | 'expression'
  subcategory: string | null
  conversation_context: string | null
}

export interface EnglishStats {
  total_corrections: number
  by_category: Record<string, number>
  last_7_days: number
}

/**
 * Get recent English corrections
 */
export async function getRecentCorrections(days: number = 7, limit: number = 20): Promise<EnglishCorrection[]> {
  const response = await fetch(
    `${API_BASE_URL}/english/corrections?days=${days}&limit=${limit}`,
    defaultFetchOptions
  )
  if (!response.ok) {
    throw new Error('Failed to fetch corrections')
  }
  return response.json()
}

/**
 * Get corrections by category
 */
export async function getCorrectionsByCategory(category: string, limit: number = 20): Promise<EnglishCorrection[]> {
  const response = await fetch(
    `${API_BASE_URL}/english/corrections/category/${category}?limit=${limit}`,
    defaultFetchOptions
  )
  if (!response.ok) {
    throw new Error('Failed to fetch corrections')
  }
  return response.json()
}

/**
 * Get English learning statistics
 */
export async function getEnglishStats(): Promise<EnglishStats> {
  const response = await fetch(`${API_BASE_URL}/english/stats`, defaultFetchOptions)
  if (!response.ok) {
    throw new Error('Failed to fetch stats')
  }
  return response.json()
}

// ============================================
// VAULT API
// ============================================

export interface VaultFile {
  path: string
  content: string
  sha: string | null
}

export interface VaultItem {
  name: string
  path: string
  type: 'file' | 'dir'
}

/**
 * Get a file from the vault
 */
export async function getVaultFile(path: string): Promise<VaultFile> {
  const response = await fetch(
    `${API_BASE_URL}/vault/file?path=${encodeURIComponent(path)}`,
    defaultFetchOptions
  )
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('File not found')
    }
    throw new Error('Failed to fetch file')
  }
  return response.json()
}

/**
 * Create a new file in the vault
 */
export async function createVaultFile(path: string, content: string): Promise<{ status: string; path: string }> {
  const response = await fetch(`${API_BASE_URL}/vault/file`, {
    ...defaultFetchOptions,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path, content }),
  })
  if (!response.ok) {
    if (response.status === 409) {
      throw new Error('File already exists')
    }
    throw new Error('Failed to create file')
  }
  return response.json()
}

/**
 * Update a file in the vault
 */
export async function updateVaultFile(
  path: string,
  content: string,
  sha: string
): Promise<{ status: string; path: string }> {
  const response = await fetch(`${API_BASE_URL}/vault/file?path=${encodeURIComponent(path)}`, {
    ...defaultFetchOptions,
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, sha }),
  })
  if (!response.ok) {
    throw new Error('Failed to update file')
  }
  return response.json()
}

/**
 * List files in a vault directory
 */
export async function listVaultDirectory(path: string = ''): Promise<VaultItem[]> {
  const response = await fetch(
    `${API_BASE_URL}/vault/directory?path=${encodeURIComponent(path)}`,
    defaultFetchOptions
  )
  if (!response.ok) {
    throw new Error('Failed to list directory')
  }
  return response.json()
}

/**
 * Search files in the vault
 */
export async function searchVault(query: string): Promise<VaultItem[]> {
  const response = await fetch(
    `${API_BASE_URL}/vault/search?query=${encodeURIComponent(query)}`,
    defaultFetchOptions
  )
  if (!response.ok) {
    throw new Error('Failed to search vault')
  }
  return response.json()
}

/**
 * Get today's daily note
 */
export async function getDailyNote(): Promise<VaultFile> {
  const response = await fetch(`${API_BASE_URL}/vault/daily-note`, defaultFetchOptions)
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Daily note not found')
    }
    throw new Error('Failed to fetch daily note')
  }
  return response.json()
}
