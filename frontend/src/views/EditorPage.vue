<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useImagesStore } from '../stores/images'

const route = useRoute()
const router = useRouter()
const imagesStore = useImagesStore()

const imageId = parseInt(route.params.id as string)
const editPrompt = ref('')
const model = ref('gemini-2.5-flash-image')
const editedImage = ref<any>(null)

onMounted(async () => {
  await imagesStore.fetchImage(imageId)
  if (imagesStore.currentImage) {
    model.value = imagesStore.currentImage.model
  }
})

async function applyEdit() {
  if (!editPrompt.value.trim()) return

  const result = await imagesStore.editImage({
    image_id: imageId,
    prompt: editPrompt.value,
    model: model.value
  })

  if (result) {
    editedImage.value = result
  }
}

function viewNewImage() {
  if (editedImage.value) {
    router.push(`/images/${editedImage.value.id}`)
  }
}
</script>

<template>
  <div class="editor-page">
    <router-link :to="`/images/${imageId}`" class="back-link">← Back to Image</router-link>

    <div class="page-header">
      <h1>Edit Image</h1>
      <p>Make modifications to your generated image</p>
    </div>

    <div v-if="imagesStore.currentImage" class="editor-container">
      <div class="comparison-section">
        <div class="image-panel original">
          <h3>Original</h3>
          <img :src="imagesStore.currentImage.image_url" :alt="imagesStore.currentImage.prompt" />
          <p class="image-prompt">{{ imagesStore.currentImage.prompt }}</p>
        </div>

        <div class="image-panel edited" v-if="editedImage">
          <h3>Edited</h3>
          <img :src="editedImage.image_url" :alt="editedImage.prompt" />
          <p class="image-prompt">{{ editedImage.prompt }}</p>
          <div class="edited-actions">
            <a :href="editedImage.image_url" download class="action-btn">Download</a>
            <button @click="viewNewImage" class="action-btn secondary">View Details</button>
          </div>
        </div>

        <div class="image-panel placeholder" v-else>
          <div class="placeholder-content">
            <span class="placeholder-icon">✨</span>
            <p>Edited image will appear here</p>
          </div>
        </div>
      </div>

      <div class="edit-form">
        <div class="form-group">
          <label>Edit Instructions</label>
          <textarea
            v-model="editPrompt"
            placeholder="Describe the changes you want to make..."
            rows="4"
            class="edit-input"
          ></textarea>
        </div>

        <div class="form-group">
          <label>Model</label>
          <select v-model="model" class="select-input">
            <option value="gemini-2.5-flash-image">Gemini Flash (Fast)</option>
            <option value="gemini-3-pro-image-preview">Gemini Pro (Advanced)</option>
          </select>
        </div>

        <div class="edit-suggestions">
          <p class="suggestions-label">Try these edits:</p>
          <div class="suggestions">
            <button @click="editPrompt = 'Add dramatic lighting'" class="suggestion">Add dramatic lighting</button>
            <button @click="editPrompt = 'Change to nighttime'" class="suggestion">Change to nighttime</button>
            <button @click="editPrompt = 'Make it more colorful'" class="suggestion">Make it more colorful</button>
            <button @click="editPrompt = 'Add a vintage filter'" class="suggestion">Add a vintage filter</button>
          </div>
        </div>

        <button
          @click="applyEdit"
          :disabled="!editPrompt.trim() || imagesStore.loading"
          class="apply-btn"
        >
          <span v-if="imagesStore.loading" class="spinner"></span>
          <span v-else>Apply Edit</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.editor-page {
  max-width: 1400px;
  margin: 0 auto;
}

.back-link {
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.875rem;
  display: inline-block;
  margin-bottom: 1rem;
}

.back-link:hover {
  color: #ffd93d;
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

.editor-container {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
}

.comparison-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.image-panel {
  background: #1a1a2e;
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid #2d2d44;
}

.image-panel h3 {
  color: #e2e8f0;
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
}

.image-panel img {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 0.75rem;
}

.image-prompt {
  color: #94a3b8;
  font-size: 0.8125rem;
  line-height: 1.4;
}

.image-panel.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.placeholder-content {
  text-align: center;
  color: #64748b;
}

.placeholder-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}

.edited-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.action-btn {
  flex: 1;
  padding: 0.5rem;
  text-align: center;
  background: #ffd93d;
  color: #1a1a2e;
  text-decoration: none;
  border: none;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
}

.action-btn.secondary {
  background: #2d2d44;
  color: #e2e8f0;
}

.edit-form {
  background: #1a1a2e;
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid #2d2d44;
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

.edit-input, .select-input {
  width: 100%;
  padding: 0.75rem;
  background: #0f0f1a;
  border: 1px solid #3d3d5c;
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 1rem;
}

.edit-input {
  resize: vertical;
  min-height: 100px;
}

.edit-input:focus, .select-input:focus {
  outline: none;
  border-color: #ffd93d;
}

.edit-suggestions {
  margin-bottom: 1.5rem;
}

.suggestions-label {
  color: #64748b;
  font-size: 0.8125rem;
  margin-bottom: 0.75rem;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.suggestion {
  padding: 0.5rem 0.75rem;
  background: #2d2d44;
  border: none;
  border-radius: 20px;
  color: #94a3b8;
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion:hover {
  background: #ffd93d;
  color: #1a1a2e;
}

.apply-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #ffd93d 0%, #ff9900 100%);
  border: none;
  border-radius: 12px;
  color: #1a1a2e;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.apply-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(255, 217, 61, 0.3);
}

.apply-btn:disabled {
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

@media (max-width: 1024px) {
  .editor-container {
    grid-template-columns: 1fr;
  }

  .comparison-section {
    grid-template-columns: 1fr;
  }
}
</style>
