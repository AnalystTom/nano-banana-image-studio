<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app">
    <nav class="navbar">
      <div class="nav-brand">
        <span class="brand-icon">🍌</span>
        <span class="brand-text">Nano Banana Studio</span>
      </div>
      <div class="nav-links">
        <RouterLink to="/" class="nav-link">Generate</RouterLink>
        <RouterLink to="/gallery" class="nav-link">Gallery</RouterLink>
        <RouterLink to="/sessions" class="nav-link">Sessions</RouterLink>
        <RouterLink to="/settings" class="nav-link">Settings</RouterLink>
      </div>
    </nav>
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand-icon {
  font-size: 1.75rem;
}

.brand-text {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #ffd93d 0%, #ff9900 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-links {
  display: flex;
  gap: 0.5rem;
}

.nav-link {
  color: #e2e8f0;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.2s ease;
  font-weight: 500;
}

.nav-link:hover {
  background: rgba(255, 217, 61, 0.1);
  color: #ffd93d;
}

.nav-link.router-link-active {
  background: rgba(255, 217, 61, 0.2);
  color: #ffd93d;
}

.main-content {
  flex: 1;
  padding: 2rem;
  background: #0f0f1a;
}
</style>
