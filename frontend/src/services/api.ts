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
  user_id?: string
  conversation_id?: string
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

// Source information from RAG retrieval
export interface Source {
  type: 'memory' | 'document' | 'uploaded_doc'
  title: string
  snippet: string
  score: number
  metadata?: {
    path?: string
    heading?: string
    memory_type?: string
    document_id?: string
    category?: string
    chunk_index?: number
  }
}

export interface StreamEvent {
  type: StreamEventType
  content?: string
  tool?: string
  success?: boolean
  tools_used?: string[] | null
  sources?: Source[] | null
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
// RAG API (Vault Indexing)
// ============================================

export interface RAGIndexStats {
  status: string
  message: string
  stats: {
    documents_indexed: number
    total_chunks: number
    cached_hashes: number
  } | null
}

export interface RAGSearchResult {
  content: string
  source: string
  source_type: 'memory' | 'document'
  score: number
}

export interface RAGSearchResponse {
  results: RAGSearchResult[]
  context: string
  stats: {
    query_length: number
    memories_searched: number
    documents_searched: number
    memories_retrieved: number
    documents_retrieved: number
    rerank_strategy: string
  }
}

/**
 * Get RAG index statistics
 */
export async function getRAGIndexStats(): Promise<RAGIndexStats> {
  const response = await fetch(`${API_BASE_URL}/rag/index/stats`, defaultFetchOptions)
  if (!response.ok) {
    throw new Error('Failed to fetch RAG stats')
  }
  return response.json()
}

/**
 * Trigger full vault indexing
 */
export async function triggerFullIndex(): Promise<RAGIndexStats> {
  const response = await fetch(`${API_BASE_URL}/rag/index/full`, {
    ...defaultFetchOptions,
    method: 'POST',
  })
  if (!response.ok) {
    throw new Error('Failed to trigger indexing')
  }
  return response.json()
}

/**
 * Trigger incremental vault indexing
 */
export async function triggerIncrementalIndex(): Promise<RAGIndexStats> {
  const response = await fetch(`${API_BASE_URL}/rag/index/incremental`, {
    ...defaultFetchOptions,
    method: 'POST',
  })
  if (!response.ok) {
    throw new Error('Failed to trigger incremental indexing')
  }
  return response.json()
}

/**
 * Search RAG system
 */
export async function searchRAG(
  query: string,
  options?: {
    userId?: string
    includeMemories?: boolean
    includeDocuments?: boolean
    limit?: number
    minScore?: number
  }
): Promise<RAGSearchResponse> {
  const response = await fetch(`${API_BASE_URL}/rag/search`, {
    ...defaultFetchOptions,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      user_id: options?.userId,
      include_memories: options?.includeMemories ?? true,
      include_documents: options?.includeDocuments ?? true,
      limit: options?.limit ?? 5,
      min_score: options?.minScore ?? 0.5,
    }),
  })
  if (!response.ok) {
    throw new Error('Failed to search RAG')
  }
  return response.json()
}

// ============================================
// MEMORY API
// ============================================

export interface Memory {
  id: string
  user_id: string
  short_text: string
  memory_type: 'preference' | 'fact' | 'task' | 'goal' | 'profile'
  timestamp: string
  last_referenced_at: string
  relevance_score: number
  num_times_referenced: number
  source: string
}

export interface MemoryListResponse {
  memories: Memory[]
  total: number
}

export interface MemoryStats {
  user_id: string
  total_memories: number
  by_type: Record<string, number>
}

/**
 * Get memories for a user
 */
export async function getUserMemories(
  userId: string,
  options?: { memoryType?: string; limit?: number }
): Promise<MemoryListResponse> {
  const params = new URLSearchParams()
  if (options?.memoryType) params.append('memory_type', options.memoryType)
  if (options?.limit) params.append('limit', options.limit.toString())

  const url = `${API_BASE_URL}/rag/memories/${userId}${params.toString() ? '?' + params : ''}`
  const response = await fetch(url, defaultFetchOptions)
  if (!response.ok) {
    throw new Error('Failed to fetch memories')
  }
  return response.json()
}

/**
 * Delete a memory
 */
export async function deleteMemory(userId: string, memoryId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/rag/memories/${userId}/${memoryId}`, {
    ...defaultFetchOptions,
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error('Failed to delete memory')
  }
}

/**
 * Get memory statistics for a user
 */
export async function getMemoryStats(userId: string): Promise<MemoryStats> {
  const response = await fetch(`${API_BASE_URL}/rag/memories/${userId}/stats`, defaultFetchOptions)
  if (!response.ok) {
    throw new Error('Failed to fetch memory stats')
  }
  return response.json()
}

// ============================================
// UPLOADED DOCUMENTS API
// ============================================

export type DocumentCategory =
  | 'manual'
  | 'invoice'
  | 'contract'
  | 'receipt'
  | 'note'
  | 'report'
  | 'guide'
  | 'reference'
  | 'personal'
  | 'work'
  | 'other'

export interface UploadedDocument {
  id: string
  user_id: string
  filename: string
  original_filename: string
  content_type: string
  category: DocumentCategory
  tags: string[]
  description: string
  file_size: number
  created_at: string
  updated_at: string
  indexed: boolean
  chunk_count: number
}

export interface DocumentListResponse {
  documents: UploadedDocument[]
  total: number
}

export interface DocumentStatsResponse {
  total_documents: number
  total_chunks: number
  total_size_bytes: number
  by_category: Record<string, number>
}

export interface DocumentSearchResult {
  chunk_id: string
  score: number
  content: string
  document_id: string
  filename: string
  category: string
  chunk_index: number
}

export interface DocumentSearchResponse {
  results: DocumentSearchResult[]
  total: number
}

export interface CategoryInfo {
  value: string
  label: string
}

/**
 * Upload a new document
 */
export async function uploadDocument(
  file: File,
  userId: string,
  category: DocumentCategory,
  tags?: string[],
  description?: string
): Promise<UploadedDocument> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('user_id', userId)
  formData.append('category', category)
  if (tags?.length) formData.append('tags', tags.join(','))
  if (description) formData.append('description', description)

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    ...defaultFetchOptions,
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || 'Failed to upload document')
  }
  return response.json()
}

/**
 * List user's documents
 */
export async function listDocuments(
  userId: string,
  options?: { category?: DocumentCategory; tags?: string[]; limit?: number }
): Promise<DocumentListResponse> {
  const params = new URLSearchParams()
  if (options?.category) params.append('category', options.category)
  if (options?.tags?.length) params.append('tags', options.tags.join(','))
  if (options?.limit) params.append('limit', options.limit.toString())

  const url = `${API_BASE_URL}/documents/${userId}${params.toString() ? '?' + params : ''}`
  const response = await fetch(url, defaultFetchOptions)
  if (!response.ok) {
    throw new Error('Failed to fetch documents')
  }
  return response.json()
}

/**
 * Get document statistics for a user
 */
export async function getDocumentStats(userId: string): Promise<DocumentStatsResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/${userId}/stats`, defaultFetchOptions)
  if (!response.ok) {
    throw new Error('Failed to fetch document stats')
  }
  return response.json()
}

/**
 * Get a specific document
 */
export async function getDocument(userId: string, documentId: string): Promise<UploadedDocument> {
  const response = await fetch(
    `${API_BASE_URL}/documents/${userId}/${documentId}`,
    defaultFetchOptions
  )
  if (!response.ok) {
    throw new Error('Failed to fetch document')
  }
  return response.json()
}

/**
 * Update document metadata
 */
export async function updateDocument(
  userId: string,
  documentId: string,
  updates: { category?: DocumentCategory; tags?: string[]; description?: string }
): Promise<UploadedDocument> {
  const response = await fetch(`${API_BASE_URL}/documents/${userId}/${documentId}`, {
    ...defaultFetchOptions,
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  })
  if (!response.ok) {
    throw new Error('Failed to update document')
  }
  return response.json()
}

/**
 * Delete a document
 */
export async function deleteDocument(userId: string, documentId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/documents/${userId}/${documentId}`, {
    ...defaultFetchOptions,
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error('Failed to delete document')
  }
}

/**
 * Search uploaded documents
 */
export async function searchDocuments(
  userId: string,
  query: string,
  options?: { category?: DocumentCategory; limit?: number; minScore?: number }
): Promise<DocumentSearchResponse> {
  const params = new URLSearchParams({ query })
  if (options?.category) params.append('category', options.category)
  if (options?.limit) params.append('limit', options.limit.toString())
  if (options?.minScore) params.append('min_score', options.minScore.toString())

  const response = await fetch(`${API_BASE_URL}/documents/${userId}/search?${params}`, {
    ...defaultFetchOptions,
    method: 'POST',
  })
  if (!response.ok) {
    throw new Error('Failed to search documents')
  }
  return response.json()
}

/**
 * Get available document categories
 */
export async function getDocumentCategories(): Promise<CategoryInfo[]> {
  const response = await fetch(`${API_BASE_URL}/documents/categories/list`, defaultFetchOptions)
  if (!response.ok) {
    throw new Error('Failed to fetch categories')
  }
  const data = await response.json()
  return data.categories
}
