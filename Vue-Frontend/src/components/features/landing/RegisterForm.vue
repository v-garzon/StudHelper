<template>
  <div class="bg-white p-8 rounded-2xl shadow-lg">
    <h2 class="text-2xl font-bold text-gray-900 mb-6">Create Account</h2>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label for="full_name" class="block text-sm font-medium text-gray-700 mb-1">
          Full Name
        </label>
        <input
          id="full_name"
          v-model="form.full_name"
          type="text"
          required
          class="input-field"
          placeholder="Enter your full name"
        />
      </div>

      <div>
        <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
          Email
        </label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          required
          class="input-field"
          placeholder="Enter your email"
        />
      </div>

      <div>
        <label for="username" class="block text-sm font-medium text-gray-700 mb-1">
          Username
        </label>
        <input
          id="username"
          v-model="form.username"
          type="text"
          required
          class="input-field"
          placeholder="Choose a username"
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
          placeholder="Create a password"
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
        <span v-if="isLoading">Creating account...</span>
        <span v-else>Register</span>
      </button>
    </form>

    <div class="mt-6 text-center space-y-2">
      <button 
        @click="$emit('switch-to-login')"
        class="text-primary-600 hover:text-primary-700 font-medium"
      >
        Already have an account? Login
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

const emit = defineEmits(['success', 'switch-to-login', 'cancel'])

const authStore = useAuthStore()
const form = ref({
  full_name: '',
  email: '',
  username: '',
  password: ''
})
const error = ref('')
const isLoading = ref(false)

const handleSubmit = async () => {
  isLoading.value = true
  error.value = ''

  console.log('Starting registration with:', form.value) // DEBUG
  
  const result = await authStore.register(form.value)
  
  console.log('Registration result:', result) // DEBUG
  console.log('Success?:', result.success) // DEBUG
  
  if (result.success) {
    console.log('Emitting success event') // DEBUG
    emit('success')
  } else {
    console.log('Registration failed:', result.message) // DEBUG
    error.value = result.message
  }
  
  isLoading.value = false
}
</script>

