<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useImagesStore } from '../stores/images'

const route = useRoute()
const router = useRouter()
const imagesStore = useImagesStore()

const imageId = parseInt(route.params.id as string)

onMounted(async () => {
  await imagesStore.fetchImage(imageId)
})

async function deleteImage() {
  if (confirm('Are you sure you want to delete this image?')) {
    const success = await imagesStore.deleteImage(imageId)
    if (success) {
      router.push('/gallery')
    }
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div class="image-detail">
    <router-link to="/gallery" class="back-link">← Back to Gallery</router-link>

    <div v-if="imagesStore.loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Loading image...</p>
    </div>

    <div v-else-if="imagesStore.currentImage" class="detail-container">
      <div class="image-section">
        <img :src="imagesStore.currentImage.image_url" :alt="imagesStore.currentImage.prompt" class="main-image" />
      </div>

      <div class="info-section">
        <h1>Image Details</h1>

        <div class="info-group">
          <label>Prompt</label>
          <p class="prompt-text">{{ imagesStore.currentImage.prompt }}</p>
        </div>

        <div class="info-grid">
          <div class="info-item">
            <label>Model</label>
            <span>{{ imagesStore.currentImage.model === 'gemini-2.5-flash-image' ? 'Gemini Flash' : 'Gemini Pro' }}</span>
          </div>
          <div class="info-item">
            <label>Aspect Ratio</label>
            <span>{{ imagesStore.currentImage.aspect_ratio }}</span>
          </div>
          <div class="info-item">
            <label>Resolution</label>
            <span>{{ imagesStore.currentImage.resolution || '1K' }}</span>
          </div>
          <div class="info-item">
            <label>Response Mode</label>
            <span>{{ imagesStore.currentImage.response_modality }}</span>
          </div>
        </div>

        <div class="info-group">
          <label>Created</label>
          <p>{{ formatDate(imagesStore.currentImage.created_at) }}</p>
        </div>

        <div class="actions">
          <a :href="imagesStore.currentImage.image_url" download class="action-btn primary">
            Download Image
          </a>
          <router-link :to="`/edit/${imageId}`" class="action-btn secondary">
            Edit Image
          </router-link>
          <button @click="deleteImage" class="action-btn danger">
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.image-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.back-link {
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.875rem;
  display: inline-block;
  margin-bottom: 1.5rem;
}

.back-link:hover {
  color: #ffd93d;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4rem;
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

.detail-container {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
}

.image-section {
  background: #1a1a2e;
  border-radius: 16px;
  padding: 1rem;
  border: 1px solid #2d2d44;
}

.main-image {
  width: 100%;
  border-radius: 12px;
}

.info-section {
  background: #1a1a2e;
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid #2d2d44;
}

.info-section h1 {
  color: #ffd93d;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
}

.info-group {
  margin-bottom: 1.5rem;
}

.info-group label {
  display: block;
  color: #64748b;
  font-size: 0.8125rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.info-group p {
  color: #e2e8f0;
  line-height: 1.5;
}

.prompt-text {
  background: #0f0f1a;
  padding: 1rem;
  border-radius: 8px;
  font-size: 0.9375rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.info-item {
  background: #0f0f1a;
  padding: 1rem;
  border-radius: 8px;
}

.info-item label {
  display: block;
  color: #64748b;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.info-item span {
  color: #e2e8f0;
  font-weight: 500;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 2rem;
}

.action-btn {
  display: block;
  padding: 0.875rem;
  text-align: center;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.primary {
  background: #ffd93d;
  color: #1a1a2e;
}

.action-btn.primary:hover {
  background: #ff9900;
}

.action-btn.secondary {
  background: #2d2d44;
  color: #e2e8f0;
}

.action-btn.secondary:hover {
  background: #3d3d5c;
}

.action-btn.danger {
  background: transparent;
  border: 1px solid #ef4444;
  color: #ef4444;
}

.action-btn.danger:hover {
  background: #ef4444;
  color: white;
}

@media (max-width: 768px) {
  .detail-container {
    grid-template-columns: 1fr;
  }
}
</style>
