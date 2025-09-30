<template>
  <SlideOutWrapper :is-visible="true" @close="$emit('close')">
    <div class="h-full flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 class="text-xl font-semibold text-gray-900">Class Information</h2>
        <button @click="$emit('close')" class="p-2 hover:bg-gray-100 rounded-lg">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">
        <!-- Basic Info -->
        <div>
          <h3 class="font-medium text-gray-900 mb-3">{{ classItem.name }}</h3>
          <p class="text-gray-600 text-sm mb-4">{{ classItem.description || 'No description provided' }}</p>
          
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-gray-500">Created:</span>
              <span class="ml-2 text-gray-900">{{ formatDate(classItem.created_at) }}</span>
            </div>
            <div>
              <span class="text-gray-500">Members:</span>
              <span class="ml-2 text-gray-900">{{ classItem.member_count || 0 }}</span>
            </div>
            <div>
              <span class="text-gray-500">Chats:</span>
              <span class="ml-2 text-gray-900">{{ classItem.chats?.length || 0 }}</span>
            </div>
            <div>
              <span class="text-gray-500">Owner:</span>
              <span class="ml-2 text-gray-900">{{ classItem.owner_name || 'You' }}</span>
            </div>
          </div>
        </div>

        <!-- Class Code -->
        <div class="bg-gray-50 p-4 rounded-lg">
          <h4 class="font-medium text-gray-900 mb-2">Class Code</h4>
          <div class="flex items-center justify-between">
            <code class="bg-white px-3 py-2 rounded border text-lg font-mono">
              {{ classItem.class_code || 'ABC123' }}
            </code>
            <button
              @click="copyClassCode"
              class="btn-secondary text-sm"
            >
              Copy
            </button>
          </div>
          <p class="text-sm text-gray-600 mt-2">
            Share this code with others to let them join your class
          </p>
        </div>

        <!-- Documents -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <h4 class="font-medium text-gray-900">Documents</h4>
            <button class="btn-secondary text-sm">
              Upload New
            </button>
          </div>
          
          <div v-if="mockDocuments.length === 0" class="text-center py-8 text-gray-500">
            <svg class="w-12 h-12 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <p>No documents uploaded yet</p>
          </div>
          
          <div v-else class="space-y-2">
            <div
              v-for="doc in mockDocuments"
              :key="doc.id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div class="flex items-center space-x-3">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ doc.name }}</p>
                  <p class="text-xs text-gray-500">{{ doc.type }} • {{ doc.size }}</p>
                </div>
              </div>
              <button class="text-gray-400 hover:text-red-600">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div>
          <h4 class="font-medium text-gray-900 mb-3">Recent Activity</h4>
          <div class="space-y-3">
            <div
              v-for="activity in mockActivity"
              :key="activity.id"
              class="flex items-start space-x-3"
            >
              <div class="w-2 h-2 bg-primary-500 rounded-full mt-2"></div>
              <div class="flex-1">
                <p class="text-sm text-gray-900">{{ activity.description }}</p>
                <p class="text-xs text-gray-500">{{ activity.time }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="border-t border-gray-200 p-6">
        <div class="flex space-x-3">
          <button class="btn-secondary flex-1">
            Class Settings
          </button>
          <button class="btn-primary flex-1">
            Invite Members
          </button>
        </div>
      </div>
    </div>
  </SlideOutWrapper>
</template>

<script setup>
import { ref } from 'vue'
import SlideOutWrapper from '@/components/ui/SlideOutWrapper.vue'

const props = defineProps({
  classItem: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])

// Mock data - replace with real API calls
const mockDocuments = ref([
  { id: 1, name: 'Chapter 1 - Introduction.pdf', type: 'PDF', size: '2.4 MB' },
  { id: 2, name: 'Lecture Notes.docx', type: 'Word', size: '1.1 MB' }
])

const mockActivity = ref([
  { id: 1, description: 'New chat session started', time: '2 hours ago' },
  { id: 2, description: 'Document uploaded: Chapter 1.pdf', time: '1 day ago' },
  { id: 3, description: 'Member joined the class', time: '2 days ago' }
])

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleDateString()
}

const copyClassCode = () => {
  const code = props.classItem.class_code || 'ABC123'
  navigator.clipboard.writeText(code)
  // You could add a toast notification here
}
</script>

