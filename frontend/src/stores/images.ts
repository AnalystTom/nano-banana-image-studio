import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Image } from '../types'
import { imagesApi, generateApi } from '../services/api'
import type { GenerateRequest, EditRequest } from '../types'

export const useImagesStore = defineStore('images', () => {
  const images = ref<Image[]>([])
  const currentImage = ref<Image | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchImages(filters?: Record<string, string | number>) {
    loading.value = true
    error.value = null
    try {
      const response = await imagesApi.list(filters)
      images.value = response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch images'
    } finally {
      loading.value = false
    }
  }

  async function fetchImage(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await imagesApi.get(id)
      currentImage.value = response.data
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch image'
      return null
    } finally {
      loading.value = false
    }
  }

  async function generateImage(request: GenerateRequest) {
    loading.value = true
    error.value = null
    try {
      const response = await generateApi.generate(request)
      images.value.unshift(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to generate image'
      return null
    } finally {
      loading.value = false
    }
  }

  async function editImage(request: EditRequest) {
    loading.value = true
    error.value = null
    try {
      const response = await generateApi.edit(request)
      images.value.unshift(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to edit image'
      return null
    } finally {
      loading.value = false
    }
  }

  async function deleteImage(id: number) {
    try {
      await imagesApi.delete(id)
      images.value = images.value.filter(img => img.id !== id)
      return true
    } catch (e: any) {
      error.value = e.message || 'Failed to delete image'
      return false
    }
  }

  return {
    images,
    currentImage,
    loading,
    error,
    fetchImages,
    fetchImage,
    generateImage,
    editImage,
    deleteImage
  }
})
