<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSessionsStore } from '../stores/sessions'
import { useRouter } from 'vue-router'

const router = useRouter()
const sessionsStore = useSessionsStore()

const showCreateModal = ref(false)
const newSessionName = ref('')
const newSessionModel = ref('gemini-2.5-flash-image')

onMounted(async () => {
  await sessionsStore.fetchSessions()
})

function openCreateModal() {
  showCreateModal.value = true
  newSessionName.value = ''
}

function closeCreateModal() {
  showCreateModal.value = false
}

async function createSession() {
  if (!newSessionName.value.trim()) return

  const session = await sessionsStore.createSession(newSessionName.value, newSessionModel.value)
  if (session) {
    closeCreateModal()
    router.push(`/sessions/${session.id}`)
  }
}

function openSession(id: number) {
  router.push(`/sessions/${id}`)
}

async function deleteSession(id: number, event: Event) {
  event.stopPropagation()
  if (confirm('Are you sure you want to delete this session?')) {
    await sessionsStore.deleteSession(id)
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}
</script>

<template>
  <div class="sessions-page">
    <div class="page-header">
      <div class="header-content">
        <h1>Sessions</h1>
        <p>Manage your image generation sessions</p>
      </div>
      <button @click="openCreateModal" class="create-btn">
        <span>+</span> New Session
      </button>
    </div>

    <div v-if="sessionsStore.loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Loading sessions...</p>
    </div>

    <div v-else-if="sessionsStore.sessions.length === 0" class="empty-state">
      <div class="empty-icon">💬</div>
      <h3>No sessions yet</h3>
      <p>Create a session to start multi-turn image generation</p>
      <button @click="openCreateModal" class="create-btn-large">Create Session</button>
    </div>

    <div v-else class="sessions-grid">
      <div
        v-for="session in sessionsStore.sessions"
        :key="session.id"
        class="session-card"
        @click="openSession(session.id)"
      >
        <div class="session-header">
          <h3>{{ session.name }}</h3>
          <button @click="deleteSession(session.id, $event)" class="delete-btn">×</button>
        </div>
        <div class="session-meta">
          <span class="meta-item">
            <span class="icon">🖼️</span>
            {{ session.image_count }} images
          </span>
          <span class="meta-item">
            <span class="icon">🤖</span>
            {{ session.model === 'gemini-2.5-flash-image' ? 'Flash' : 'Pro' }}
          </span>
        </div>
        <div class="session-footer">
          <span class="date">Created {{ formatDate(session.created_at) }}</span>
        </div>
      </div>
    </div>

    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
      <div class="modal">
        <h2>Create New Session</h2>
        <div class="form-group">
          <label>Session Name</label>
          <input
            v-model="newSessionName"
            type="text"
            placeholder="Enter session name..."
            class="text-input"
            @keyup.enter="createSession"
          />
        </div>
        <div class="form-group">
          <label>Model</label>
          <select v-model="newSessionModel" class="select-input">
            <option value="gemini-2.5-flash-image">Gemini Flash (Fast)</option>
            <option value="gemini-3-pro-image-preview">Gemini Pro (Advanced)</option>
          </select>
        </div>
        <div class="modal-actions">
          <button @click="closeCreateModal" class="cancel-btn">Cancel</button>
          <button @click="createSession" :disabled="!newSessionName.trim()" class="confirm-btn">
            Create
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sessions-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.create-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #ffd93d;
  border: none;
  border-radius: 8px;
  color: #1a1a2e;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.create-btn:hover {
  background: #ff9900;
  transform: translateY(-2px);
}

.create-btn span {
  font-size: 1.25rem;
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
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

.create-btn-large {
  padding: 1rem 2rem;
  background: #ffd93d;
  border: none;
  border-radius: 8px;
  color: #1a1a2e;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
}

.sessions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.session-card {
  background: #1a1a2e;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #2d2d44;
  cursor: pointer;
  transition: all 0.3s;
}

.session-card:hover {
  border-color: #ffd93d;
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(255, 217, 61, 0.15);
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.session-header h3 {
  color: #e2e8f0;
  font-size: 1.125rem;
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

.session-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #94a3b8;
  font-size: 0.875rem;
}

.meta-item .icon {
  font-size: 1rem;
}

.session-footer {
  padding-top: 1rem;
  border-top: 1px solid #2d2d44;
}

.date {
  color: #64748b;
  font-size: 0.8125rem;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: #1a1a2e;
  border-radius: 16px;
  padding: 2rem;
  width: 100%;
  max-width: 400px;
  border: 1px solid #2d2d44;
}

.modal h2 {
  color: #ffd93d;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  color: #e2e8f0;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.text-input, .select-input {
  width: 100%;
  padding: 0.75rem;
  background: #0f0f1a;
  border: 1px solid #3d3d5c;
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 1rem;
}

.text-input:focus, .select-input:focus {
  outline: none;
  border-color: #ffd93d;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.cancel-btn, .confirm-btn {
  flex: 1;
  padding: 0.75rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background: transparent;
  border: 1px solid #3d3d5c;
  color: #94a3b8;
}

.cancel-btn:hover {
  border-color: #ffd93d;
  color: #ffd93d;
}

.confirm-btn {
  background: #ffd93d;
  border: none;
  color: #1a1a2e;
}

.confirm-btn:hover:not(:disabled) {
  background: #ff9900;
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
