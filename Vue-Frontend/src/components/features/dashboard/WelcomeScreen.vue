<template>
  <div class="h-full flex items-center justify-center bg-gray-50">
    <div class="text-center max-w-md">
      <div class="mb-8">
        <svg class="w-16 h-16 mx-auto text-primary-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
        </svg>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">Welcome to StudHelper</h2>
        <p class="text-gray-600">Your personal AI study assistant</p>
      </div>

      <div class="space-y-4">
        <div v-if="classes.length === 0" class="bg-white p-6 rounded-lg shadow-sm">
          <h3 class="font-semibold text-gray-900 mb-2">Get Started</h3>
          <p class="text-gray-600 mb-4">Create your first study class to begin learning with AI</p>
          <button
            @click="createClass"
            class="btn-primary"
          >
            Create Your First Class
          </button>
        </div>

        <div v-else class="bg-white p-6 rounded-lg shadow-sm">
          <h3 class="font-semibold text-gray-900 mb-2">Ready to Study?</h3>
          <p class="text-gray-600 mb-4">Select a class from the sidebar or start a new chat session</p>
          
          <div class="space-y-2">
            <div class="text-sm text-gray-500">
              <strong>{{ classes.length }}</strong> classes created
            </div>
            <div class="text-sm text-gray-500">
              <strong>{{ totalChats }}</strong> chat sessions
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <button
            @click="createClass"
            class="bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow"
          >
            <svg class="w-8 h-8 text-primary-600 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            <p class="font-medium text-gray-900">New Class</p>
            <p class="text-sm text-gray-600">Create a study class</p>
          </button>

          <router-link
            to="/help"
            class="bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow block"
          >
            <svg class="w-8 h-8 text-primary-600 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p class="font-medium text-gray-900">Get Help</p>
            <p class="text-sm text-gray-600">Learn how to use StudHelper</p>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useUIStore } from '@/stores/ui'
import { useClassStore } from '@/stores/classes'

const uiStore = useUIStore()
const classStore = useClassStore()

const { classes } = storeToRefs(classStore)

const totalChats = computed(() => {
  return classes.value.reduce((total, classItem) => {
    return total + (classItem.chats?.length || 0)
  }, 0)
})

const createClass = () => {
  uiStore.openModal('CreateClassModal')
}
</script>

