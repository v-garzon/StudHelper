<template>
    <div class="bg-white p-8 rounded-2xl shadow-lg">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Login to StudHelper</h2>
      
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700 mb-1">
            Username or Email
          </label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            required
            class="input-field"
            placeholder="Enter your username or email"
          />
        </div>
  
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
            Password
          </label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            class="input-field"
            placeholder="Enter your password"
          />
        </div>
  
        <div v-if="error" class="text-red-600 text-sm">
          {{ error }}
        </div>
  
        <button 
          type="submit" 
          :disabled="isLoading"
          class="w-full btn-primary"
        >
          <span v-if="isLoading">Logging in...</span>
          <span v-else>Login</span>
        </button>
      </form>
  
      <div class="mt-6 text-center space-y-2">
        <button 
          @click="$emit('switch-to-register')"
          class="text-primary-600 hover:text-primary-700 font-medium"
        >
          Don't have an account? Register
        </button>
        <br>
        <button 
          @click="$emit('cancel')"
          class="text-gray-600 hover:text-gray-700"
        >
          Back
        </button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { useAuthStore } from '@/stores/auth'
  
  const emit = defineEmits(['success', 'switch-to-register', 'cancel'])
  
  const authStore = useAuthStore()
  const form = ref({
    username: '',  // Changed from 'email' to 'username'
    password: ''
  })
  const error = ref('')
  const isLoading = ref(false)
  
  const handleSubmit = async () => {
  isLoading.value = true
  error.value = ''

  const result = await authStore.login({
    email: form.value.username,  // Pass username/email value
    password: form.value.password // Add password!
  })
  
  if (result.success) {
    emit('success')
  } else {
    error.value = result.message
  }
  
  isLoading.value = false
}
  </script>