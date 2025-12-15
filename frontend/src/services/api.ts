import axios from 'axios'
import type { Image, Session, ConversationMessage, Settings, Template, GenerateRequest, EditRequest } from '../types'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

export const generateApi = {
  generate: (data: GenerateRequest) => api.post<Image>('/generate', data),
  edit: (data: EditRequest) => api.post<Image>('/edit', data)
}

export const sessionsApi = {
  list: () => api.get<Session[]>('/sessions'),
  get: (id: number) => api.get<Session>(`/sessions/${id}`),
  create: (data: { name: string; model: string }) => api.post<Session>('/sessions', data),
  update: (id: number, data: { name: string }) => api.put<Session>(`/sessions/${id}`, data),
  delete: (id: number) => api.delete(`/sessions/${id}`),
  getHistory: (id: number) => api.get<ConversationMessage[]>(`/sessions/${id}/history`),
  sendMessage: (id: number, message: string) => api.post<Image>(`/sessions/${id}/message`, { message })
}

export const imagesApi = {
  list: (params?: Record<string, string | number>) => api.get<Image[]>('/images', { params }),
  get: (id: number) => api.get<Image>(`/images/${id}`),
  getVersions: (id: number) => api.get(`/images/${id}/versions`),
  delete: (id: number) => api.delete(`/images/${id}`),
  bulkDelete: (ids: number[]) => api.delete('/images/bulk', { data: ids })
}

export const settingsApi = {
  get: () => api.get<Settings>('/settings'),
  update: (data: Partial<Settings>) => api.put<Settings>('/settings', data)
}

export const templatesApi = {
  list: () => api.get<Template[]>('/templates'),
  create: (data: { name: string; category: string; template: string; description?: string }) =>
    api.post<Template>('/templates', data),
  delete: (id: number) => api.delete(`/templates/${id}`)
}

export default api
