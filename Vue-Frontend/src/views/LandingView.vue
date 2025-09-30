<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-white">
    <!-- Navigation -->
    <nav class="relative z-10 p-6">
      <div class="flex justify-between items-center max-w-7xl mx-auto">
        <h1 class="text-2xl font-bold text-gray-900">StudHelper</h1>
        <router-link to="/help" class="text-gray-600 hover:text-gray-900 font-medium">
          Help
        </router-link>
      </div>
    </nav>

    <!-- Hero Section -->
    <div class="flex items-center justify-center min-h-[calc(100vh-100px)]">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 max-w-6xl mx-auto px-6">
        
        <!-- Auth Section -->
        <div class="flex flex-col justify-center">
          <div v-if="!showForm" class="space-y-6">
            <div class="text-center lg:text-left">
              <h2 class="text-4xl font-bold text-gray-900 mb-4">
                Welcome to StudHelper
              </h2>
              <p class="text-xl text-gray-600">
                Your personal AI study assistant
              </p>
            </div>
            
            <div class="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <button 
                @click="showLoginForm"
                class="btn-primary px-8 py-3 text-lg"
              >
                Login
              </button>
              <button 
                @click="showRegisterForm"
                class="btn-secondary px-8 py-3 text-lg"
              >
                Register
              </button>
            </div>
          </div>

          <!-- Auth Forms -->
          <div v-else class="w-full max-w-md mx-auto lg:mx-0">
            <LoginForm 
              v-if="formType === 'login'" 
              @success="handleAuthSuccess"
              @switch-to-register="showRegisterForm"
              @cancel="hideForm"
            />
            <RegisterForm 
              v-if="formType === 'register'" 
              @success="handleAuthSuccess"
              @switch-to-login="showLoginForm"
              @cancel="hideForm"
            />
          </div>
        </div>

        <!-- Branding Section -->
        <div class="flex flex-col justify-center text-center lg:text-left">
          <div class="bg-white p-8 rounded-2xl shadow-lg">
            <h3 class="text-2xl font-bold text-gray-900 mb-4">
              AI-Powered Learning
            </h3>
            <p class="text-gray-600 mb-6">
              Upload your study materials and chat with an AI tutor that understands your specific content.
            </p>
            <div class="space-y-3 text-left">
              <div class="flex items-center space-x-3">
                <div class="w-2 h-2 bg-primary-500 rounded-full"></div>
                <span class="text-gray-700">Upload PDFs, documents, and videos</span>
              </div>
              <div class="flex items-center space-x-3">
                <div class="w-2 h-2 bg-primary-500 rounded-full"></div>
                <span class="text-gray-700">Create organized study classes</span>
              </div>
              <div class="flex items-center space-x-3">
                <div class="w-2 h-2 bg-primary-500 rounded-full"></div>
                <span class="text-gray-700">Chat with AI about your materials</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Scroll indicator -->
    <div class="fixed bottom-8 left-1/2 transform -translate-x-1/2 text-gray-400">
      <div class="animate-bounce">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // ADD THIS
import LoginForm from '@/components/features/landing/LoginForm.vue'
import RegisterForm from '@/components/features/landing/RegisterForm.vue'

const router = useRouter()
const authStore = useAuthStore() // ADD THIS
const showForm = ref(false)
const formType = ref('login')

const showLoginForm = () => {
  formType.value = 'login'
  showForm.value = true
}

const showRegisterForm = () => {
  formType.value = 'register'
  showForm.value = true
}

const hideForm = () => {
  showForm.value = false
}

// const handleAuthSuccess = () => {
//   router.push({ name: 'Dashboard' })
// }
// test function for development
const handleAuthSuccess = async () => {
  console.log('Auth success handler called')
  console.log('Is authenticated:', authStore.isAuthenticated)
  console.log('User:', authStore.user)
  console.log('Token:', authStore.token)
  
  // Small delay to ensure state is updated
  await new Promise(resolve => setTimeout(resolve, 100))
  
  console.log('After delay - Is authenticated:', authStore.isAuthenticated)
  
  router.push({ name: 'Dashboard' })
}
</script>

