export interface Image {
  id: number
  filename: string
  image_url: string
  prompt: string
  model: string
  aspect_ratio: string
  resolution: string | null
  response_modality: string
  text_response?: string
  created_at: string
}

export interface Session {
  id: number
  name: string
  model: string
  created_at: string
  updated_at: string
  image_count: number
}

export interface ConversationMessage {
  id: number
  role: 'user' | 'assistant'
  message: string | null
  image_id: number | null
  image_url: string | null
  created_at: string
}

export interface Settings {
  default_model: string
  default_aspect_ratio: string
  default_resolution: string
  default_response_modality: string
  google_search_default: boolean
  auto_save_conversations: boolean
}

export interface Template {
  id: number
  name: string
  category: string
  template: string
  description: string | null
  created_at: string
}

export interface GenerateRequest {
  prompt: string
  model: string
  aspect_ratio: string
  resolution: string
  response_modality: string
  google_search_enabled: boolean
  session_id?: number
}

export interface EditRequest {
  image_id: number
  prompt: string
  model: string
  aspect_ratio?: string
  resolution?: string
}
