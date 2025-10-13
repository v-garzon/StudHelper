<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="p-4 border-b border-gray-200">
      <div v-if="sidebarExpanded" class="flex items-center justify-between">
        <h2 class="font-semibold text-gray-900">Classes</h2>
        <button 
          @click="openCreateClassModal"
          class="p-1 rounded-md hover:bg-gray-100"
          title="Create New Class"
        >
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
        </button>
      </div>
      <div v-else class="flex justify-center">
        <button 
          @click="openCreateClassModal"
          class="p-1 rounded-md hover:bg-gray-100"
          title="Create New Class"
        >
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
        </button>
      </div>
    </div>

    <!-- Classes List -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="isLoading" class="p-4">
        <div class="animate-pulse space-y-2">
          <div class="h-4 bg-gray-200 rounded"></div>
          <div class="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>

      <div v-else-if="classes.length === 0" class="p-4 text-center text-gray-500">
        <div v-if="sidebarExpanded">
          <p class="mb-2">No classes yet</p>
          <button @click="openCreateClassModal" class="text-primary-600 hover:text-primary-700">
            Create your first class
          </button>
        </div>
      </div>

      <div v-else class="p-2 space-y-1">
        <div 
          v-for="classItem in classes" 
          :key="classItem.id"
          class="group"
        >
          <!-- Class Item -->
          <div 
            :class="[
              'flex items-center p-2 rounded-lg cursor-pointer transition-colors',
              currentClass?.id === classItem.id ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-50'
            ]"
            @click="selectClass(classItem)"
          >
            <button
              @click.stop="toggleClassExpansion(classItem.id)"
              class="mr-2 p-1"
            >
              <svg 
                :class="[
                  'w-4 h-4 transition-transform',
                  expandedClasses.includes(classItem.id) ? 'rotate-90' : ''
                ]"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </button>
            
            <div v-if="sidebarExpanded" class="flex-1 min-w-0">
              <p class="text-sm font-medium truncate">{{ classItem.name }}</p>
              <p class="text-xs text-gray-500">{{ classItem.chat_session_count || 0 }} chats</p>
            </div>
            
            <div v-if="sidebarExpanded" class="flex space-x-1 opacity-0 group-hover:opacity-100">
              <button
                @click.stop="createNewChat(classItem)"
                class="p-1 rounded hover:bg-gray-200"
                title="New Chat"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                </svg>
              </button>
              <button
                @click.stop="openClassInfo(classItem)"
                class="p-1 rounded hover:bg-gray-200"
                title="Class Info"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </button>
            </div>
          </div>

          <!-- Chats List -->
          <div 
            v-if="expandedClasses.includes(classItem.id) && sidebarExpanded"
            class="ml-6 space-y-1"
          >
            <div
              v-for="chat in classItem.chats || []"
              :key="chat.id"
              :class="[
                'flex items-center p-2 rounded-lg cursor-pointer text-sm transition-colors',
                currentChat?.id === chat.id ? 'bg-primary-100 text-primary-800' : 'hover:bg-gray-50'
              ]"
              @click="selectChat(chat)"
            >
              <svg class="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
              </svg>
              <span class="truncate">{{ chat.title || 'New Chat' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useUIStore } from '@/stores/ui'
import { useClassStore } from '@/stores/classes'

const uiStore = useUIStore()
const classStore = useClassStore()

const { sidebarExpanded } = storeToRefs(uiStore)
const { classes, currentClass, currentChat, isLoading } = storeToRefs(classStore)

const expandedClasses = ref([])

const toggleClassExpansion = (classId) => {
  const index = expandedClasses.value.indexOf(classId)
  if (index > -1) {
    expandedClasses.value.splice(index, 1)
  } else {
    expandedClasses.value.push(classId)
  }
}

const selectClass = (classItem) => {
  classStore.selectClass(classItem)
  if (!expandedClasses.value.includes(classItem.id)) {
    expandedClasses.value.push(classItem.id)
  }
}

const selectChat = (chat) => {
  classStore.selectChat(chat)
}

const openCreateClassModal = () => {
  uiStore.openModal('ClassModal', { mode: 'create' })
}

const createNewChat = (classItem) => {
  // PLACEHOLDER - Phase 4
  console.log('Creating new chat for class:', classItem.name)
  alert('Chat creation coming in Phase 4!')
}

const openClassInfo = (classItem) => {
  // Open ClassModal in edit mode
  uiStore.openModal('ClassModal', { 
    mode: 'edit', 
    classId: classItem.id 
  })
}

onMounted(() => {
  classStore.fetchClasses()
})
</script>


