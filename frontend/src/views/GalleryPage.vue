<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useImagesStore } from '../stores/images'
import { useRouter } from 'vue-router'

const router = useRouter()
const imagesStore = useImagesStore()

const filterModel = ref('')
const filterAspectRatio = ref('')
const sortBy = ref('newest')

const aspectRatios = ['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9']

onMounted(async () => {
  await imagesStore.fetchImages()
})

const filteredImages = computed(() => {
  let result = [...imagesStore.images]

  if (filterModel.value) {
    result = result.filter(img => img.model === filterModel.value)
  }

  if (filterAspectRatio.value) {
    result = result.filter(img => img.aspect_ratio === filterAspectRatio.value)
  }

  return result
})

async function applyFilters() {
  const params: Record<string, string> = {}
  if (filterModel.value) params.model = filterModel.value
  if (filterAspectRatio.value) params.aspect_ratio = filterAspectRatio.value
  params.sort_by = sortBy.value
  await imagesStore.fetchImages(params)
}

function clearFilters() {
  filterModel.value = ''
  filterAspectRatio.value = ''
  sortBy.value = 'newest'
  imagesStore.fetchImages()
}

function viewImage(id: number) {
  router.push(`/images/${id}`)
}
</script>

<template>
  <div class="gallery-page">
    <div class="page-header">
      <h1>Image Gallery</h1>
      <p>Browse and manage your generated images</p>
    </div>

    <div class="gallery-layout">
      <aside class="filter-panel">
        <h3>Filters</h3>

        <div class="filter-group">
          <label>Model</label>
          <select v-model="filterModel" class="filter-select">
            <option value="">All Models</option>
            <option value="gemini-2.5-flash-image">Gemini Flash</option>
            <option value="gemini-3-pro-image-preview">Gemini Pro</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Aspect Ratio</label>
          <select v-model="filterAspectRatio" class="filter-select">
            <option value="">All Ratios</option>
            <option v-for="ar in aspectRatios" :key="ar" :value="ar">{{ ar }}</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Sort By</label>
          <select v-model="sortBy" class="filter-select">
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
          </select>
        </div>

        <div class="filter-actions">
          <button @click="applyFilters" class="apply-btn">Apply Filters</button>
          <button @click="clearFilters" class="clear-btn">Clear</button>
        </div>
      </aside>

      <main class="gallery-content">
        <div v-if="imagesStore.loading" class="loading">
          <div class="loading-spinner"></div>
          <p>Loading images...</p>
        </div>

        <div v-else-if="filteredImages.length === 0" class="empty-state">
          <div class="empty-icon">🖼️</div>
          <h3>No images yet</h3>
          <p>Generate your first image to see it here!</p>
          <router-link to="/" class="generate-link">Generate Image</router-link>
        </div>

        <div v-else class="image-grid">
          <div
            v-for="image in filteredImages"
            :key="image.id"
            class="image-card"
            @click="viewImage(image.id)"
          >
            <div class="image-wrapper">
              <img :src="image.image_url" :alt="image.prompt" />
              <div class="image-overlay">
                <span class="view-text">View Details</span>
              </div>
            </div>
            <div class="image-info">
              <p class="image-prompt">{{ image.prompt.substring(0, 50) }}...</p>
              <div class="image-meta">
                <span class="meta-tag">{{ image.aspect_ratio }}</span>
                <span class="meta-tag">{{ image.resolution || '1K' }}</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.gallery-page {
  max-width: 1600px;
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

.gallery-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
}

.filter-panel {
  background: #1a1a2e;
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid #2d2d44;
  height: fit-content;
  position: sticky;
  top: 2rem;
}

.filter-panel h3 {
  color: #ffd93d;
  margin-bottom: 1.5rem;
}

.filter-group {
  margin-bottom: 1.25rem;
}

.filter-group label {
  display: block;
  color: #e2e8f0;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.filter-select {
  width: 100%;
  padding: 0.75rem;
  background: #0f0f1a;
  border: 1px solid #3d3d5c;
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 0.875rem;
}

.filter-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.apply-btn {
  padding: 0.75rem;
  background: #ffd93d;
  border: none;
  border-radius: 8px;
  color: #1a1a2e;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.apply-btn:hover {
  background: #ff9900;
}

.clear-btn {
  padding: 0.75rem;
  background: transparent;
  border: 1px solid #3d3d5c;
  border-radius: 8px;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-btn:hover {
  border-color: #ffd93d;
  color: #ffd93d;
}

.gallery-content {
  min-height: 400px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  background: #1a1a2e;
  border-radius: 16px;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #e2e8f0;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #64748b;
  margin-bottom: 1.5rem;
}

.generate-link {
  padding: 0.75rem 1.5rem;
  background: #ffd93d;
  color: #1a1a2e;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.image-card {
  background: #1a1a2e;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #2d2d44;
  cursor: pointer;
  transition: all 0.3s;
}

.image-card:hover {
  transform: translateY(-4px);
  border-color: #ffd93d;
  box-shadow: 0 8px 30px rgba(255, 217, 61, 0.15);
}

.image-wrapper {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.image-card:hover .image-wrapper img {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-card:hover .image-overlay {
  opacity: 1;
}

.view-text {
  color: #ffd93d;
  font-weight: 600;
  padding: 0.5rem 1rem;
  border: 2px solid #ffd93d;
  border-radius: 8px;
}

.image-info {
  padding: 1rem;
}

.image-prompt {
  color: #e2e8f0;
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
  line-height: 1.4;
}

.image-meta {
  display: flex;
  gap: 0.5rem;
}

.meta-tag {
  padding: 0.25rem 0.5rem;
  background: #2d2d44;
  border-radius: 4px;
  color: #94a3b8;
  font-size: 0.75rem;
}

@media (max-width: 768px) {
  .gallery-layout {
    grid-template-columns: 1fr;
  }

  .filter-panel {
    position: static;
  }
}
</style>
