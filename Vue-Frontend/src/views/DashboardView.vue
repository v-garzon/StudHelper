<template>
  <div class="h-screen flex bg-gray-50">
    <!-- Sidebar -->
    <div :class="[
      'bg-white border-r border-gray-200 transition-all duration-300',
      sidebarExpanded ? 'w-80' : 'w-16'
    ]">
      <Sidebar />
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col">
      <!-- Header -->
      <header class="bg-white border-b border-gray-200 px-6 py-4">
        <div class="flex justify-between items-center">
          <div class="flex items-center space-x-4">
            <button 
              @click="toggleSidebar"
              class="p-2 rounded-lg hover:bg-gray-100"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
              </svg>
            </button>
            <h1 class="text-xl font-semibold text-gray-900">
                {{ selectedClass ? selectedClass.name : 'StudHelper Dashboard' }}
            </h1>
          </div>
          
          <UserMenu />
        </div>
      </header>

      <!-- Content Area -->
      <main class="flex-1 overflow-hidden relative">
        <!-- Verification Banner -->
        <VerificationBanner />
        
        <!-- Dynamic Content Based on State -->
        <ChatInterface v-if="currentChat" />
        <ClassWelcome
            v-else-if="selectedClass"
            variant="class-selected"
            :class-name="selectedClass.name"
            :class-description="selectedClass.description"
            :document-count="selectedClass.document_count || 0"
            :session-count="selectedClass.chat_session_count || 0"
            />
        <ClassGrid 
          v-else-if="hasClasses"
          :classes="classes"
        />
        <ClassWelcome 
          v-else
          variant="no-classes"
        />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useUIStore } from '@/stores/ui'
import { useClassStore } from '@/stores/classes'
import Sidebar from '@/components/features/dashboard/Sidebar.vue'
import UserMenu from '@/components/features/dashboard/UserMenu.vue'
import ChatInterface from '@/components/features/dashboard/ChatInterface.vue'
import ClassWelcome from '@/components/features/class-management/views/ClassWelcome.vue'
import ClassGrid from '@/components/features/class-management/views/ClassGrid.vue'
import VerificationBanner from '@/components/features/dashboard/VerificationBanner.vue'

const uiStore = useUIStore()
const classStore = useClassStore()

const { sidebarExpanded } = storeToRefs(uiStore)
const { classes, selectedClass, currentChat, hasClasses } = storeToRefs(classStore)

const toggleSidebar = () => {
  uiStore.toggleSidebar()
}
</script>


