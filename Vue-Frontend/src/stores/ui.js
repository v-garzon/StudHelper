import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUIStore = defineStore('ui', () => {
  const activeModal = ref(null)
  const activeSlideOut = ref(null)
  const sidebarExpanded = ref(true)

  const openModal = (modalName, props = {}) => {
    activeModal.value = { name: modalName, props }
  }

  const closeModal = () => {
    activeModal.value = null
  }

  const openSlideOut = (slideOutName, props = {}) => {
    activeSlideOut.value = { name: slideOutName, props }
  }

  const closeSlideOut = () => {
    activeSlideOut.value = null
  }

  const toggleSidebar = () => {
    sidebarExpanded.value = !sidebarExpanded.value
  }

  return {
    activeModal,
    activeSlideOut,
    sidebarExpanded,
    openModal,
    closeModal,
    openSlideOut,
    closeSlideOut,
    toggleSidebar
  }
})

