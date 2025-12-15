<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSettingsStore } from '../stores/settings'

const settingsStore = useSettingsStore()

const defaultModel = ref('gemini-2.5-flash-image')
const defaultAspectRatio = ref('1:1')
const defaultResolution = ref('1K')
const defaultResponseModality = ref('TEXT_IMAGE')
const googleSearchDefault = ref(false)
const autoSaveConversations = ref(true)

const saveMessage = ref('')
const showSaveMessage = ref(false)

const aspectRatios = ['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9']
const resolutions = ['1K', '2K', '4K']

onMounted(async () => {
  await settingsStore.fetchSettings()
  await settingsStore.fetchTemplates()

  defaultModel.value = settingsStore.settings.default_model
  defaultAspectRatio.value = settingsStore.settings.default_aspect_ratio
  defaultResolution.value = settingsStore.settings.default_resolution
  defaultResponseModality.value = settingsStore.settings.default_response_modality
  googleSearchDefault.value = settingsStore.settings.google_search_default
  autoSaveConversations.value = settingsStore.settings.auto_save_conversations
})

async function saveSettings() {
  const success = await settingsStore.updateSettings({
    default_model: defaultModel.value,
    default_aspect_ratio: defaultAspectRatio.value,
    default_resolution: defaultResolution.value,
    default_response_modality: defaultResponseModality.value,
    google_search_default: googleSearchDefault.value,
    auto_save_conversations: autoSaveConversations.value
  })

  if (success) {
    saveMessage.value = 'Settings saved successfully!'
    showSaveMessage.value = true
    setTimeout(() => {
      showSaveMessage.value = false
    }, 3000)
  }
}

async function deleteTemplate(id: number) {
  if (confirm('Are you sure you want to delete this template?')) {
    await settingsStore.deleteTemplate(id)
  }
}
</script>

<template>
  <div class="settings-page">
    <div class="page-header">
      <h1>Settings</h1>
      <p>Configure your default preferences</p>
    </div>

    <div class="settings-container">
      <section class="settings-section">
        <h2>Default Generation Settings</h2>

        <div class="settings-grid">
          <div class="setting-group">
            <label>Default Model</label>
            <select v-model="defaultModel" class="select-input">
              <option value="gemini-2.5-flash-image">Gemini Flash (Fast, 1K)</option>
              <option value="gemini-3-pro-image-preview">Gemini Pro (Advanced, up to 4K)</option>
            </select>
          </div>

          <div class="setting-group">
            <label>Default Aspect Ratio</label>
            <select v-model="defaultAspectRatio" class="select-input">
              <option v-for="ar in aspectRatios" :key="ar" :value="ar">{{ ar }}</option>
            </select>
          </div>

          <div class="setting-group">
            <label>Default Resolution</label>
            <select v-model="defaultResolution" class="select-input">
              <option v-for="res in resolutions" :key="res" :value="res">{{ res }}</option>
            </select>
          </div>

          <div class="setting-group">
            <label>Default Response Mode</label>
            <select v-model="defaultResponseModality" class="select-input">
              <option value="TEXT_IMAGE">Text + Image</option>
              <option value="IMAGE">Image Only</option>
            </select>
          </div>
        </div>

        <div class="checkbox-settings">
          <label class="checkbox-label">
            <input type="checkbox" v-model="googleSearchDefault" />
            <span>Enable Google Search Grounding by default (Pro only)</span>
          </label>

          <label class="checkbox-label">
            <input type="checkbox" v-model="autoSaveConversations" />
            <span>Auto-save conversations</span>
          </label>
        </div>

        <button @click="saveSettings" class="save-btn" :disabled="settingsStore.loading">
          <span v-if="settingsStore.loading">Saving...</span>
          <span v-else>Save Settings</span>
        </button>

        <div v-if="showSaveMessage" class="save-message">
          {{ saveMessage }}
        </div>
      </section>

      <section class="settings-section">
        <h2>Prompt Templates</h2>
        <p class="section-description">Manage your saved prompt templates</p>

        <div v-if="settingsStore.templates.length === 0" class="empty-templates">
          <p>No custom templates yet. Default templates are provided for common use cases.</p>
        </div>

        <div v-else class="templates-list">
          <div
            v-for="template in settingsStore.templates"
            :key="template.id"
            class="template-item"
          >
            <div class="template-info">
              <h3>{{ template.name }}</h3>
              <span class="template-category">{{ template.category }}</span>
              <p class="template-preview">{{ template.template.substring(0, 80) }}...</p>
            </div>
            <button @click="deleteTemplate(template.id)" class="delete-btn">×</button>
          </div>
        </div>
      </section>

      <section class="settings-section">
        <h2>About</h2>
        <div class="about-info">
          <p><strong>Nano Banana Image Studio</strong></p>
          <p>Version 1.0.0</p>
          <p class="about-description">
            AI-powered image generation and editing studio using Gemini's Nano Banana API.
            Create, edit, and manage AI-generated images with multi-turn conversations.
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.settings-page {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  color: #ffd93d;
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.page-header p {
  color: #94a3b8;
}

.settings-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.settings-section {
  background: #1a1a2e;
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid #2d2d44;
}

.settings-section h2 {
  color: #ffd93d;
  font-size: 1.25rem;
  margin-bottom: 1rem;
}

.section-description {
  color: #64748b;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.setting-group {
  display: flex;
  flex-direction: column;
}

.setting-group label {
  color: #e2e8f0;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.select-input {
  padding: 0.75rem;
  background: #0f0f1a;
  border: 1px solid #3d3d5c;
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 0.9375rem;
}

.select-input:focus {
  outline: none;
  border-color: #ffd93d;
}

.checkbox-settings {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #94a3b8;
  cursor: pointer;
}

.checkbox-label input {
  width: 18px;
  height: 18px;
  accent-color: #ffd93d;
}

.save-btn {
  padding: 0.875rem 2rem;
  background: #ffd93d;
  border: none;
  border-radius: 8px;
  color: #1a1a2e;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.save-btn:hover:not(:disabled) {
  background: #ff9900;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.save-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid #22c55e;
  border-radius: 8px;
  color: #22c55e;
  font-size: 0.875rem;
}

.empty-templates {
  padding: 2rem;
  text-align: center;
  color: #64748b;
  background: #0f0f1a;
  border-radius: 8px;
}

.templates-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.template-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem;
  background: #0f0f1a;
  border-radius: 8px;
  border: 1px solid #2d2d44;
}

.template-info h3 {
  color: #e2e8f0;
  font-size: 1rem;
  margin-bottom: 0.25rem;
}

.template-category {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  background: #2d2d44;
  border-radius: 4px;
  color: #94a3b8;
  font-size: 0.75rem;
  margin-bottom: 0.5rem;
}

.template-preview {
  color: #64748b;
  font-size: 0.8125rem;
}

.delete-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid #3d3d5c;
  border-radius: 6px;
  color: #64748b;
  font-size: 1.25rem;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-btn:hover {
  background: #ef4444;
  border-color: #ef4444;
  color: white;
}

.about-info {
  color: #e2e8f0;
}

.about-info p {
  margin-bottom: 0.5rem;
}

.about-info strong {
  color: #ffd93d;
}

.about-description {
  color: #94a3b8;
  font-size: 0.875rem;
  line-height: 1.5;
  margin-top: 1rem;
}

@media (max-width: 640px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
