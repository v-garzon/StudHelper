<template>
  <div class="class-grid-container p-8">
    <div class="grid-header flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-900">Your Classes</h2>
      <button 
        @click="openCreateClassModal"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
      >
        + New Class
      </button>
    </div>

    <div class="class-grid grid grid-cols-2 gap-6">
      <div 
        v-for="classItem in classes" 
        :key="classItem.id"
        class="class-card p-6 bg-white border border-gray-200 rounded-lg cursor-pointer hover:border-primary-400 hover:shadow-lg transition-all duration-200 transform hover:-translate-y-1"
        @click="selectClass(classItem)"
      >
        <div class="card-icon text-4xl mb-3">📚</div>
        <h3 class="card-title text-xl font-semibold text-gray-900 mb-2">
          {{ classItem.name }}
        </h3>
        <p class="card-description text-gray-600 mb-4 line-clamp-2">
          {{ classItem.description || 'No description' }}
        </p>
        <div class="card-footer flex items-center text-sm text-gray-500">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
          </svg>
          <span>{{ classItem.chat_session_count || 0 }} chat sessions</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useClassStore } from '@/stores/classes'
import { useUIStore } from '@/stores/ui'

defineProps({
  classes: {
    type: Array,
    required: true
  }
})

const classStore = useClassStore()
const uiStore = useUIStore()

function selectClass(classItem) {
  classStore.selectClass(classItem)
}

function openCreateClassModal() {
  uiStore.openModal('ClassModal', { mode: 'create' })
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>


