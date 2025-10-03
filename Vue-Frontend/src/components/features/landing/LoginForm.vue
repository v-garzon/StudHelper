<template>
  <div class="bg-white p-8 rounded-2xl shadow-lg">
    <h2 class="text-2xl font-bold text-gray-900 mb-6">Login</h2>
    
    <!-- OAuth Buttons -->
    <div class="space-y-3 mb-6">
      <button
        @click="handleGoogleLogin"
        :disabled="isLoading"
        class="w-full flex items-center justify-center gap-3 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg class="w-5 h-5" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
        <span class="text-gray-700 font-medium">Continue with Google</span>
      </button>

      <button
        @click="handleMicrosoftLogin"
        :disabled="isLoading"
        class="w-full flex items-center justify-center gap-3 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg class="w-5 h-5" viewBox="0 0 23 23">
          <path fill="#f3f3f3" d="M0 0h23v23H0z"/>
          <path fill="#f35325" d="M1 1h10v10H1z"/>
          <path fill="#81bc06" d="M12 1h10v10H12z"/>
          <path fill="#05a6f0" d="M1 12h10v10H1z"/>
          <path fill="#ffba08" d="M12 12h10v10H12z"/>
        </svg>
        <span class="text-gray-700 font-medium">Continue with Microsoft</span>
      </button>
    </div>

    <div class="relative mb-6">
      <div class="absolute inset-0 flex items-center">
        <div class="w-full border-t border-gray-300"></div>
      </div>
      <div class="relative flex justify-center text-sm">
        <span class="px-2 bg-white text-gray-500">Or continue with email</span>
      </div>
    </div>
    
    <!-- Email/Password Form -->
    <form @submit.prevent="handleEmailLogin" class="space-y-4">
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
        @click="handleForgotPassword"
        class="text-primary-600 hover:text-primary-700 text-sm"
      >
        Forgot password?
      </button>
      <br>
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
import { 
  auth, 
  googleProvider, 
  microsoftProvider, 
  signInWithPopup,
  signInWithEmailAndPassword,
  sendPasswordResetEmail
} from '@/config/firebase'

const emit = defineEmits(['success', 'switch-to-register', 'cancel'])

const authStore = useAuthStore()
const form = ref({
  email: '',
  password: ''
})
const error = ref('')
const isLoading = ref(false)

// Email/Password Login
const handleEmailLogin = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    // Firebase authenticates
    const userCredential = await signInWithEmailAndPassword(
      auth,
      form.value.email,
      form.value.password
    )
    
    // Get Firebase ID token
    const idToken = await userCredential.user.getIdToken()
    
    // Send to backend (no username/full_name needed - existing user)
    const result = await authStore.firebaseLogin(idToken)
    
    if (result.success) {
      emit('success')
    } else {
      error.value = result.message
    }
  } catch (err) {
    console.error('Login error:', err)
    if (err.code === 'auth/user-not-found') {
      error.value = 'No account found with this email'
    } else if (err.code === 'auth/wrong-password') {
      error.value = 'Incorrect password'
    } else if (err.code === 'auth/too-many-requests') {
      error.value = 'Too many failed attempts. Try again later.'
    } else if (err.code === 'auth/invalid-credential') {
      error.value = 'Invalid email or password'
    } else {
      error.value = err.message || 'Login failed'
    }
  } finally {
    isLoading.value = false
  }
}

// Google OAuth
const handleGoogleLogin = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    const result = await signInWithPopup(auth, googleProvider)
    const idToken = await result.user.getIdToken()
    
    const loginResult = await authStore.firebaseLogin(idToken)
    
    if (loginResult.success) {
      emit('success')
    } else {
      error.value = loginResult.message
    }
  } catch (err) {
    console.error('Google login error:', err)
    if (err.code === 'auth/popup-closed-by-user') {
      error.value = 'Sign-in cancelled'
    } else {
      error.value = err.message || 'Google login failed'
    }
  } finally {
    isLoading.value = false
  }
}

// Microsoft OAuth
const handleMicrosoftLogin = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    const result = await signInWithPopup(auth, microsoftProvider)
    const idToken = await result.user.getIdToken()
    
    const loginResult = await authStore.firebaseLogin(idToken)
    
    if (loginResult.success) {
      emit('success')
    } else {
      error.value = loginResult.message
    }
  } catch (err) {
    console.error('Microsoft login error:', err)
    if (err.code === 'auth/popup-closed-by-user') {
      error.value = 'Sign-in cancelled'
    } else {
      error.value = err.message || 'Microsoft login failed'
    }
  } finally {
    isLoading.value = false
  }
}

// Password Reset
const handleForgotPassword = async () => {
  const email = prompt('Enter your email address:')
  if (!email) return
  
  try {
    await sendPasswordResetEmail(auth, email)
    alert('Password reset email sent! Check your inbox.')
  } catch (err) {
    alert('Error: ' + (err.message || 'Could not send reset email'))
  }
}
</script>


