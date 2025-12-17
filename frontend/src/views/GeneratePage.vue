<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useImagesStore } from '../stores/images'
import { useSettingsStore } from '../stores/settings'

const imagesStore = useImagesStore()
const settingsStore = useSettingsStore()

const mediaType = ref<'image' | 'video'>('image')
const prompt = ref('')
const model = ref('gemini-2.5-flash-image')
const aspectRatio = ref('1:1')
const resolution = ref('1K')
const responseModality = ref('TEXT_IMAGE')
const googleSearchEnabled = ref(false)
const duration = ref('5s')
const generatedImage = ref<any>(null)
const generatedVideo = ref<any>(null)

const imageAspectRatios = ['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9']
const videoAspectRatios = ['16:9', '9:16']
const resolutions = ['1K', '2K', '4K']
const durations = ['5s', '8s']
const imageModels = [
  { value: 'gemini-2.5-flash-image', label: 'Gemini Flash (Fast, 1K)' },
  { value: 'gemini-3-pro-image-preview', label: 'Gemini Pro (Advanced, up to 4K)' }
]
const videoModels = [
  { value: 'veo-3.0-generate-preview', label: 'Veo 3.0 (Preview)' }
]

const currentAspectRatios = computed(() => mediaType.value === 'image' ? imageAspectRatios : videoAspectRatios)
const currentModels = computed(() => mediaType.value === 'image' ? imageModels : videoModels)

function switchMediaType(type: 'image' | 'video') {
  mediaType.value = type
  if (type === 'video') {
    model.value = 'veo-3.0-generate-preview'
    aspectRatio.value = '16:9'
  } else {
    model.value = settingsStore.settings.default_model || 'gemini-2.5-flash-image'
    aspectRatio.value = settingsStore.settings.default_aspect_ratio || '1:1'
  }
}

onMounted(async () => {
  await settingsStore.fetchSettings()
  await settingsStore.fetchTemplates()
  model.value = settingsStore.settings.default_model
  aspectRatio.value = settingsStore.settings.default_aspect_ratio
  resolution.value = settingsStore.settings.default_resolution
  responseModality.value = settingsStore.settings.default_response_modality
  googleSearchEnabled.value = settingsStore.settings.google_search_default
})

async function generate() {
  if (!prompt.value.trim()) return

  if (mediaType.value === 'image') {
    const result = await imagesStore.generateImage({
      prompt: prompt.value,
      model: model.value,
      aspect_ratio: aspectRatio.value,
      resolution: resolution.value,
      response_modality: responseModality.value,
      google_search_enabled: googleSearchEnabled.value
    })

    if (result) {
      generatedImage.value = result
      generatedVideo.value = null
    }
  } else {
    const result = await imagesStore.generateVideo({
      prompt: prompt.value,
      model: model.value,
      aspect_ratio: aspectRatio.value,
      duration: duration.value
    })

    if (result) {
      generatedVideo.value = result
      generatedImage.value = null
    }
  }
}

function useTemplate(template: string) {
  prompt.value = template
}
</script>

<template>
  <div class="generate-page">
    <div class="page-header">
      <h1>Generate {{ mediaType === 'image' ? 'Image' : 'Video' }}</h1>
      <p>Create stunning AI-generated {{ mediaType === 'image' ? 'images' : 'videos' }} with Nano Banana</p>
    </div>

    <div class="generate-container">
      <div class="form-section">
        <div class="media-toggle">
          <button
            :class="['toggle-btn', { active: mediaType === 'image' }]"
            @click="switchMediaType('image')"
          >
            Image
          </button>
          <button
            :class="['toggle-btn', { active: mediaType === 'video' }]"
            @click="switchMediaType('video')"
          >
            Video
          </button>
        </div>

        <div class="form-group">
          <label>Prompt</label>
          <textarea
            v-model="prompt"
            placeholder="Describe the image you want to create..."
            rows="4"
            class="prompt-input"
          ></textarea>
        </div>

        <div class="templates-section" v-if="settingsStore.templates.length">
          <label>Quick Templates</label>
          <div class="templates-grid">
            <button
              v-for="template in settingsStore.templates"
              :key="template.id"
              @click="useTemplate(template.template)"
              class="template-btn"
            >
              {{ template.name }}
            </button>
          </div>
        </div>

        <div class="options-grid">
          <div class="form-group">
            <label>Model</label>
            <select v-model="model" class="select-input">
              <option v-for="m in currentModels" :key="m.value" :value="m.value">
                {{ m.label }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Aspect Ratio</label>
            <select v-model="aspectRatio" class="select-input">
              <option v-for="ar in currentAspectRatios" :key="ar" :value="ar">{{ ar }}</option>
            </select>
          </div>

          <div class="form-group" v-if="mediaType === 'image'">
            <label>Resolution</label>
            <select v-model="resolution" class="select-input" :disabled="model !== 'gemini-3-pro-image-preview'">
              <option v-for="res in resolutions" :key="res" :value="res">{{ res }}</option>
            </select>
          </div>

          <div class="form-group" v-if="mediaType === 'video'">
            <label>Duration</label>
            <select v-model="duration" class="select-input">
              <option v-for="d in durations" :key="d" :value="d">{{ d }}</option>
            </select>
          </div>

          <div class="form-group" v-if="mediaType === 'image'">
            <label>Response Mode</label>
            <select v-model="responseModality" class="select-input">
              <option value="TEXT_IMAGE">Text + Image</option>
              <option value="IMAGE">Image Only</option>
            </select>
          </div>
        </div>

        <div class="form-group checkbox-group" v-if="mediaType === 'image'">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="googleSearchEnabled"
              :disabled="model !== 'gemini-3-pro-image-preview'"
            />
            <span>Enable Google Search Grounding (Pro only)</span>
          </label>
        </div>

        <button
          @click="generate"
          :disabled="!prompt.trim() || imagesStore.loading"
          class="generate-btn"
        >
          <span v-if="imagesStore.loading" class="spinner"></span>
          <span v-else>Generate {{ mediaType === 'image' ? 'Image' : 'Video' }}</span>
        </button>
      </div>

      <div class="result-section">
        <div v-if="imagesStore.loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Generating your {{ mediaType }}...</p>
        </div>

        <div v-else-if="generatedImage && mediaType === 'image'" class="result-display">
          <img :src="generatedImage.image_url" :alt="generatedImage.prompt" class="result-image" />
          <div class="result-meta">
            <h3>Generated Image</h3>
            <p><strong>Prompt:</strong> {{ generatedImage.prompt }}</p>
            <p><strong>Model:</strong> {{ generatedImage.model }}</p>
            <p><strong>Aspect Ratio:</strong> {{ generatedImage.aspect_ratio }}</p>
            <p><strong>Resolution:</strong> {{ generatedImage.resolution }}</p>
            <div v-if="generatedImage.text_response" class="text-response">
              <strong>Response:</strong>
              <p>{{ generatedImage.text_response }}</p>
            </div>
            <div class="result-actions">
              <a :href="generatedImage.image_url" download class="action-btn">Download</a>
              <router-link :to="`/images/${generatedImage.id}`" class="action-btn secondary">
                View Details
              </router-link>
            </div>
          </div>
        </div>

        <div v-else-if="generatedVideo && mediaType === 'video'" class="result-display">
          <img :src="generatedVideo.video_url" :alt="generatedVideo.prompt" class="result-video" />
          <div class="result-meta">
            <h3>Generated Video</h3>
            <p><strong>Prompt:</strong> {{ generatedVideo.prompt }}</p>
            <p><strong>Model:</strong> {{ generatedVideo.model }}</p>
            <p><strong>Aspect Ratio:</strong> {{ generatedVideo.aspect_ratio }}</p>
            <p><strong>Duration:</strong> {{ generatedVideo.duration }}</p>
            <div class="result-actions">
              <a :href="generatedVideo.video_url" download class="action-btn">Download</a>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <div class="empty-icon">{{ mediaType === 'image' ? '🎨' : '🎬' }}</div>
          <p>Your generated {{ mediaType }} will appear here</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.generate-page {
  max-width: 1400px;
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

.generate-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.form-section, .result-section {
  background: #1a1a2e;
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid #2d2d44;
}

.media-toggle {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  background: #0f0f1a;
  padding: 0.25rem;
  border-radius: 12px;
}

.toggle-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: #94a3b8;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn.active {
  background: linear-gradient(135deg, #ffd93d 0%, #ff9900 100%);
  color: #1a1a2e;
}

.toggle-btn:not(.active):hover {
  background: #2d2d44;
  color: #e2e8f0;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  color: #e2e8f0;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.prompt-input, .select-input {
  width: 100%;
  padding: 0.75rem;
  background: #0f0f1a;
  border: 1px solid #3d3d5c;
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.prompt-input:focus, .select-input:focus {
  outline: none;
  border-color: #ffd93d;
}

.prompt-input {
  resize: vertical;
  min-height: 100px;
}

.templates-section {
  margin-bottom: 1.25rem;
}

.templates-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.template-btn {
  padding: 0.5rem 1rem;
  background: #2d2d44;
  border: none;
  border-radius: 20px;
  color: #e2e8f0;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.template-btn:hover {
  background: #ffd93d;
  color: #1a1a2e;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.checkbox-group {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  color: #94a3b8;
}

.checkbox-label input {
  width: 18px;
  height: 18px;
  accent-color: #ffd93d;
}

.generate-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #ffd93d 0%, #ff9900 100%);
  border: none;
  border-radius: 12px;
  color: #1a1a2e;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(255, 217, 61, 0.3);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #1a1a2e;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #94a3b8;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid #2d2d44;
  border-top-color: #ffd93d;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.result-display {
  display: flex;
  flex-direction: column;
}

.result-image, .result-video {
  width: 100%;
  border-radius: 12px;
  margin-bottom: 1rem;
}

.result-meta {
  color: #e2e8f0;
}

.result-meta h3 {
  color: #ffd93d;
  margin-bottom: 0.75rem;
}

.result-meta p {
  margin-bottom: 0.5rem;
  color: #94a3b8;
}

.result-meta p strong {
  color: #e2e8f0;
}

.text-response {
  background: #0f0f1a;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.result-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.action-btn {
  flex: 1;
  padding: 0.75rem;
  text-align: center;
  background: #ffd93d;
  color: #1a1a2e;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s;
}

.action-btn.secondary {
  background: #2d2d44;
  color: #e2e8f0;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #64748b;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .generate-container {
    grid-template-columns: 1fr;
  }

  .options-grid {
    grid-template-columns: 1fr;
  }
}
</style>
