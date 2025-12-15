<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useSessionsStore } from '../stores/sessions'

const route = useRoute()
const sessionsStore = useSessionsStore()

const sessionId = parseInt(route.params.id as string)
const newMessage = ref('')

onMounted(async () => {
  await sessionsStore.fetchSession(sessionId)
  await sessionsStore.fetchHistory(sessionId)
})

async function sendMessage() {
  if (!newMessage.value.trim()) return

  const message = newMessage.value
  newMessage.value = ''

  await sessionsStore.sendMessage(sessionId, message)
}
</script>

<template>
  <div class="session-detail">
    <div class="session-header" v-if="sessionsStore.currentSession">
      <router-link to="/sessions" class="back-link">← Back to Sessions</router-link>
      <h1>{{ sessionsStore.currentSession.name }}</h1>
      <p class="session-meta">
        Model: {{ sessionsStore.currentSession.model === 'gemini-2.5-flash-image' ? 'Gemini Flash' : 'Gemini Pro' }}
        | {{ sessionsStore.currentSession.image_count }} images
      </p>
    </div>

    <div class="conversation-container">
      <div class="conversation-thread">
        <div v-if="sessionsStore.conversationHistory.length === 0" class="empty-conversation">
          <div class="empty-icon">💬</div>
          <p>Start the conversation by sending a message below</p>
        </div>

        <div
          v-for="message in sessionsStore.conversationHistory"
          :key="message.id"
          :class="['message', message.role]"
        >
          <div class="message-avatar">
            {{ message.role === 'user' ? '👤' : '🍌' }}
          </div>
          <div class="message-content">
            <p v-if="message.message" class="message-text">{{ message.message }}</p>
            <div v-if="message.image_url" class="message-image">
              <img :src="message.image_url" alt="Generated image" />
              <a :href="message.image_url" download class="download-btn">Download</a>
            </div>
          </div>
        </div>

        <div v-if="sessionsStore.loading" class="generating-indicator">
          <div class="loading-spinner"></div>
          <span>Generating...</span>
        </div>
      </div>

      <div class="message-input-container">
        <textarea
          v-model="newMessage"
          placeholder="Describe what you want to generate or how to modify the image..."
          rows="3"
          class="message-input"
          @keydown.enter.ctrl="sendMessage"
        ></textarea>
        <button
          @click="sendMessage"
          :disabled="!newMessage.trim() || sessionsStore.loading"
          class="send-btn"
        >
          <span v-if="sessionsStore.loading" class="spinner"></span>
          <span v-else>Send</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.session-detail {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 140px);
}

.session-header {
  margin-bottom: 1.5rem;
}

.back-link {
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.875rem;
  display: inline-block;
  margin-bottom: 0.5rem;
}

.back-link:hover {
  color: #ffd93d;
}

.session-header h1 {
  color: #ffd93d;
  font-size: 1.75rem;
  margin-bottom: 0.5rem;
}

.session-meta {
  color: #64748b;
  font-size: 0.875rem;
}

.conversation-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #1a1a2e;
  border-radius: 16px;
  border: 1px solid #2d2d44;
  overflow: hidden;
}

.conversation-thread {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.empty-conversation {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: #64748b;
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.message {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #2d2d44;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
}

.message.user .message-content {
  text-align: right;
}

.message-text {
  background: #2d2d44;
  padding: 1rem;
  border-radius: 12px;
  color: #e2e8f0;
  line-height: 1.5;
}

.message.user .message-text {
  background: #3d3d5c;
}

.message-image {
  margin-top: 0.75rem;
  position: relative;
  display: inline-block;
}

.message-image img {
  max-width: 100%;
  border-radius: 12px;
}

.download-btn {
  position: absolute;
  bottom: 0.75rem;
  right: 0.75rem;
  padding: 0.5rem 1rem;
  background: rgba(0, 0, 0, 0.7);
  color: #ffd93d;
  text-decoration: none;
  border-radius: 6px;
  font-size: 0.8125rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.message-image:hover .download-btn {
  opacity: 1;
}

.generating-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  color: #94a3b8;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #2d2d44;
  border-top-color: #ffd93d;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.message-input-container {
  padding: 1rem;
  border-top: 1px solid #2d2d44;
  display: flex;
  gap: 1rem;
}

.message-input {
  flex: 1;
  padding: 0.75rem;
  background: #0f0f1a;
  border: 1px solid #3d3d5c;
  border-radius: 8px;
  color: #e2e8f0;
  resize: none;
  font-size: 1rem;
}

.message-input:focus {
  outline: none;
  border-color: #ffd93d;
}

.send-btn {
  padding: 0 1.5rem;
  background: #ffd93d;
  border: none;
  border-radius: 8px;
  color: #1a1a2e;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 80px;
}

.send-btn:hover:not(:disabled) {
  background: #ff9900;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid #1a1a2e;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
</style>
