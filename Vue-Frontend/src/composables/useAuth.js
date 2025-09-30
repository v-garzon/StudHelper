import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useAuth() {
  const authStore = useAuthStore()
  
  const user = computed(() => authStore.user)
  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const isLoading = computed(() => authStore.isLoading)
  
  const login = async (credentials) => {
    return await authStore.login(credentials)
  }
  
  const register = async (userData) => {
    return await authStore.register(userData)
  }
  
  const logout = () => {
    authStore.logout()
  }
  
  const updateProfile = async (profileData) => {
    return await authStore.updateProfile(profileData)
  }
  
  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    updateProfile
  }
}

