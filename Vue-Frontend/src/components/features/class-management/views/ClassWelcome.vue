<template>
  <div class="class-welcome flex items-center justify-center h-full bg-gray-50 p-8">
    <!-- No Classes Variant -->
    <div v-if="variant === 'no-classes'" class="text-center max-w-md">
      <div class="welcome-icon text-6xl mb-4">🎓</div>
      <h1 class="text-3xl font-bold text-gray-900 mb-3">Welcome to StudHelper!</h1>
      <p class="text-lg text-gray-600 mb-6">
        Create your first class to get started with AI-powered learning.
      </p>
      <button 
        @click="openCreateClassModal"
        class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-lg font-medium"
      >
        + Create Your First Class
      </button>
    </div>

    <!-- Class Selected Variant -->
    <div v-else-if="variant === 'class-selected'" class="text-center max-w-2xl">
      <div class="class-header mb-8">
        <div class="class-icon text-5xl mb-3">📚</div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ className }}</h1>
        <p class="text-lg text-gray-600">{{ classDescription || 'No description provided' }}</p>
      </div>

      <div class="welcome-message mb-6">
        <h2 class="text-2xl font-semibold text-gray-800 mb-2">Ready to learn?</h2>
        <p class="text-gray-600">
          Create a new chat session to start asking questions about your materials.
        </p>
      </div>

      <button 
        @click="createChatSession"
        disabled
        class="px-6 py-3 bg-gray-400 text-white rounded-lg cursor-not-allowed inline-flex items-center space-x-2"
      >
        <span>+ New Chat Session</span>
        <span class="px-2 py-0.5 bg-gray-600 rounded text-xs">Phase 4</span>
      </button>

      <div class="class-stats mt-8 flex justify-center space-x-8">
        <div class="stat text-center">
          <div class="stat-value text-2xl font-bold text-primary-600">{{ documentCount }}</div>
          <div class="stat-label text-sm text-gray-600">Documents</div>
        </div>
        <div class="stat text-center">
          <div class="stat-value text-2xl font-bold text-primary-600">{{ sessionCount }}</div>
          <div class="stat-label text-sm text-gray-600">Chat Sessions</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useUIStore } from '@/stores/ui'

defineProps({
  variant: {
    type: String,
    required: true,
    validator: (value) => ['no-classes', 'class-selected'].includes(value)
  },
  className: {
    type: String,
    default: ''
  },
  classDescription: {
    type: String,
    default: ''
  },
  documentCount: {
    type: Number,
    default: 0
  },
  sessionCount: {
    type: Number,
    default: 0
  }
})

const uiStore = useUIStore()

function openCreateClassModal() {
  uiStore.openModal('ClassModal', { mode: 'create' })
}

function createChatSession() {
  // PLACEHOLDER - Phase 4
  console.log('Chat session creation coming in Phase 4')
}
</script>


