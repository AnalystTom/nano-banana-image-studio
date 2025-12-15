import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'generate',
      component: () => import('../views/GeneratePage.vue')
    },
    {
      path: '/gallery',
      name: 'gallery',
      component: () => import('../views/GalleryPage.vue')
    },
    {
      path: '/sessions',
      name: 'sessions',
      component: () => import('../views/SessionsPage.vue')
    },
    {
      path: '/sessions/:id',
      name: 'session-detail',
      component: () => import('../views/SessionDetail.vue')
    },
    {
      path: '/images/:id',
      name: 'image-detail',
      component: () => import('../views/ImageDetail.vue')
    },
    {
      path: '/edit/:id',
      name: 'editor',
      component: () => import('../views/EditorPage.vue')
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsPage.vue')
    }
  ]
})

export default router
