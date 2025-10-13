<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <router-view />
    <ModalManager />
    <SlideOutManager />
    
    <!-- Global modal container -->
    <div id="modal-container"></div>
    
    <!-- Global slide-out container -->
    <div id="slideout-container"></div>
    
    <!-- Global overlay container -->
    <div id="overlay-container"></div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import ModalManager from '@/components/ui/ModalManager.vue'
import SlideOutManager from '@/components/ui/SlideOutManager.vue'

const authStore = useAuthStore()

onMounted(() => {
  // Try to restore user session on app load
  authStore.initializeAuth()
})
</script>

