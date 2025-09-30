import { computed } from 'vue'
import { useUIStore } from '@/stores/ui'

export function useUI() {
  const uiStore = useUIStore()
  
  const activeModal = computed(() => uiStore.activeModal)
  const activeSlideOut = computed(() => uiStore.activeSlideOut)
  const sidebarExpanded = computed(() => uiStore.sidebarExpanded)
  
  const openModal = (modalName, props = {}) => {
    uiStore.openModal(modalName, props)
  }
  
  const closeModal = () => {
    uiStore.closeModal()
  }
  
  const openSlideOut = (slideOutName, props = {}) => {
    uiStore.openSlideOut(slideOutName, props)
  }
  
  const closeSlideOut = () => {
    uiStore.closeSlideOut()
  }
  
  const toggleSidebar = () => {
    uiStore.toggleSidebar()
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
}

