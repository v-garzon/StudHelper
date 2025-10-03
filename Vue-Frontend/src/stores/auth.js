import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/auth/authService'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  const login = async (credentials) => {
    isLoading.value = true
    try {
      const response = await authService.login(credentials)
      token.value = response.data.access_token
      user.value = response.data.user
      localStorage.setItem('token', token.value)
      return { success: true }
    } catch (error) {
      return { success: false, message: error.response?.data?.message || 'Login failed' }
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData) => {
    isLoading.value = true
    try {
      console.log('Register: Creating account...') // DEBUG
      
      // First, create the account
      const registerResponse = await authService.register(userData)
      console.log('Register: Account created:', registerResponse.data) // DEBUG
      
      // Registration successful, now login to get token
      console.log('Register: Logging in...') // DEBUG
      const loginResponse = await authService.login({
        email: userData.email,
        password: userData.password
      })
      console.log('Register: Login response:', loginResponse.data) // DEBUG
      
      // Store token and user data
      token.value = loginResponse.data.access_token
      user.value = loginResponse.data.user || registerResponse.data
      localStorage.setItem('token', token.value)
      
      console.log('Register: Success! Token:', token.value) // DEBUG
      console.log('Register: User:', user.value) // DEBUG
      
      return { success: true }
    } catch (error) {
      console.error('Register: Error occurred:', error) // DEBUG
      console.error('Register: Error response:', error.response) // DEBUG
      return { 
        success: false, 
        message: error.response?.data?.detail || error.response?.data?.message || 'Registration failed' 
      }
    } finally {
      isLoading.value = false
    }
  }

  // NEW: Firebase authentication
  const firebaseLogin = async (data) => {
    isLoading.value = true
    try {
      // data can be just idToken string OR { idToken, username, full_name }
      const payload = typeof data === 'string' 
        ? { id_token: data }
        : { 
            id_token: data.idToken,
            username: data.username,
            full_name: data.full_name
          }
      
      const response = await authService.firebaseLogin(payload)
      token.value = response.data.access_token
      user.value = response.data.user
      localStorage.setItem('token', token.value)
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Firebase login failed' 
      }
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  const initializeAuth = async () => {
    if (token.value) {
      try {
        const response = await authService.getCurrentUser()
        user.value = response.data
      } catch (error) {
        logout()
      }
    }
  }

  return {
    user,
    token,
    isLoading,
    isAuthenticated,
    login,
    register,
    firebaseLogin,  // NEW
    logout,
    initializeAuth
  }
})


