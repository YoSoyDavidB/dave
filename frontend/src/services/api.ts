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
}

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

export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/health`)
  return response.json()
}
