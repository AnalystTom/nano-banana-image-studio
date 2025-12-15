import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Session, ConversationMessage, Image } from '../types'
import { sessionsApi } from '../services/api'

export const useSessionsStore = defineStore('sessions', () => {
  const sessions = ref<Session[]>([])
  const currentSession = ref<Session | null>(null)
  const conversationHistory = ref<ConversationMessage[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchSessions() {
    loading.value = true
    error.value = null
    try {
      const response = await sessionsApi.list()
      sessions.value = response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch sessions'
    } finally {
      loading.value = false
    }
  }

  async function fetchSession(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await sessionsApi.get(id)
      currentSession.value = response.data
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch session'
      return null
    } finally {
      loading.value = false
    }
  }

  async function fetchHistory(sessionId: number) {
    loading.value = true
    error.value = null
    try {
      const response = await sessionsApi.getHistory(sessionId)
      conversationHistory.value = response.data
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch history'
      return []
    } finally {
      loading.value = false
    }
  }

  async function createSession(name: string, model: string = 'gemini-2.5-flash-image') {
    loading.value = true
    error.value = null
    try {
      const response = await sessionsApi.create({ name, model })
      sessions.value.unshift(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to create session'
      return null
    } finally {
      loading.value = false
    }
  }

  async function updateSession(id: number, name: string) {
    try {
      const response = await sessionsApi.update(id, { name })
      const index = sessions.value.findIndex(s => s.id === id)
      if (index !== -1) {
        sessions.value[index] = response.data
      }
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to update session'
      return null
    }
  }

  async function deleteSession(id: number) {
    try {
      await sessionsApi.delete(id)
      sessions.value = sessions.value.filter(s => s.id !== id)
      return true
    } catch (e: any) {
      error.value = e.message || 'Failed to delete session'
      return false
    }
  }

  async function sendMessage(sessionId: number, message: string): Promise<Image | null> {
    loading.value = true
    error.value = null
    try {
      const response = await sessionsApi.sendMessage(sessionId, message)
      await fetchHistory(sessionId)
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to send message'
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    sessions,
    currentSession,
    conversationHistory,
    loading,
    error,
    fetchSessions,
    fetchSession,
    fetchHistory,
    createSession,
    updateSession,
    deleteSession,
    sendMessage
  }
})
