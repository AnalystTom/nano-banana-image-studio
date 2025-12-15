import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Settings, Template } from '../types'
import { settingsApi, templatesApi } from '../services/api'

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<Settings>({
    default_model: 'gemini-2.5-flash-image',
    default_aspect_ratio: '1:1',
    default_resolution: '1K',
    default_response_modality: 'TEXT_IMAGE',
    google_search_default: false,
    auto_save_conversations: true
  })
  const templates = ref<Template[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchSettings() {
    loading.value = true
    error.value = null
    try {
      const response = await settingsApi.get()
      settings.value = response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch settings'
    } finally {
      loading.value = false
    }
  }

  async function updateSettings(data: Partial<Settings>) {
    loading.value = true
    error.value = null
    try {
      const response = await settingsApi.update(data)
      settings.value = response.data
      return true
    } catch (e: any) {
      error.value = e.message || 'Failed to update settings'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchTemplates() {
    loading.value = true
    error.value = null
    try {
      const response = await templatesApi.list()
      templates.value = response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch templates'
    } finally {
      loading.value = false
    }
  }

  async function createTemplate(data: { name: string; category: string; template: string; description?: string }) {
    try {
      const response = await templatesApi.create(data)
      templates.value.push(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to create template'
      return null
    }
  }

  async function deleteTemplate(id: number) {
    try {
      await templatesApi.delete(id)
      templates.value = templates.value.filter(t => t.id !== id)
      return true
    } catch (e: any) {
      error.value = e.message || 'Failed to delete template'
      return false
    }
  }

  return {
    settings,
    templates,
    loading,
    error,
    fetchSettings,
    updateSettings,
    fetchTemplates,
    createTemplate,
    deleteTemplate
  }
})
