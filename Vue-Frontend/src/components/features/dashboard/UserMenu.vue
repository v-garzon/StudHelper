<template>
  <div class="relative">
    <button
      @click="toggleMenu"
      class="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100 transition-colors"
    >
      <!-- User Name (only show if enough space - hidden on mobile) -->
      <span 
        v-if="displayName" 
        class="hidden lg:block text-sm font-medium text-gray-700 max-w-[150px] truncate"
      >
        {{ displayName }}
      </span>
      
      <!-- User Avatar Circle -->
      <div class="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-semibold">
        {{ userInitial }}
      </div>
      
      <!-- Dropdown Arrow -->
      <svg 
        :class="['w-4 h-4 text-gray-500 transition-transform', isOpen ? 'rotate-180' : '']" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
      </svg>
    </button>

    <!-- Dropdown Menu -->
    <transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        class="absolute right-0 mt-2 w-56 rounded-lg shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50"
      >
        <div class="py-1">
          <!-- User Info -->
          <div class="px-4 py-3 border-b border-gray-100">
            <p class="text-sm font-medium text-gray-900">{{ fullDisplayName }}</p>
            <p class="text-xs text-gray-500 truncate">{{ userEmail }}</p>
          </div>

          <!-- Menu Items -->
          <button
            @click="handleProfile"
            class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>
            <span>Profile Settings</span>
          </button>

          <button
            @click="handleSettings"
            class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            <span>Settings</span>
          </button>

          <div class="border-t border-gray-100"></div>

          <button
            @click="handleLogout"
            class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
            </svg>
            <span>Logout</span>
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const isOpen = ref(false)

const displayName = computed(() => authStore.displayName)
const fullDisplayName = computed(() => authStore.displayName || 'User')
const userEmail = computed(() => authStore.user?.email || '')
const userInitial = computed(() => {
  const name = authStore.displayName || authStore.user?.email || 'U'
  return name.charAt(0).toUpperCase()
})

const toggleMenu = () => {
  isOpen.value = !isOpen.value
}

const closeMenu = () => {
  isOpen.value = false
}

const handleProfile = () => {
  closeMenu()
  // TODO: Navigate to profile page
  console.log('Profile clicked')
}

const handleSettings = () => {
  closeMenu()
  // TODO: Navigate to settings page
  console.log('Settings clicked')
}

const handleLogout = async () => {
  closeMenu()
  authStore.logout()
  router.push({ name: 'Landing' })
}

// Close menu when clicking outside
const handleClickOutside = (event) => {
  const target = event.target
  if (!target.closest('.relative')) {
    closeMenu()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>


# ============================================================================
# BACKEND FILES
# ============================================================================

