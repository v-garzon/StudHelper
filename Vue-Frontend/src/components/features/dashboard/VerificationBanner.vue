<template>
    <div 
      v-if="shouldShowBanner" 
      class="absolute top-0 left-0 right-0 bg-yellow-50 border-l-4 border-yellow-400 p-4 shadow-md z-50 animate-slideDown"
    >
      <div class="flex justify-between items-start">
        <div class="flex items-start">
          <svg 
            class="h-6 w-6 text-yellow-400 mr-3 flex-shrink-0 mt-0.5" 
            viewBox="0 0 20 20" 
            fill="currentColor"
          >
            <path 
              fill-rule="evenodd" 
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
            />
          </svg>
          <div class="flex-1">
            <h3 class="text-sm font-medium text-yellow-800 mb-1">
              Email Verification Required
            </h3>
            <p class="text-sm text-yellow-700 mb-3">
              Please verify your email address to unlock all features and ensure account security.
              Check your inbox for the verification link.
            </p>
            <div class="flex items-center space-x-4">
              <button
                @click="resendVerification"
                :disabled="isResending || cooldownActive"
                class="text-sm font-medium text-yellow-800 hover:text-yellow-900 underline disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ buttonText }}
              </button>
              <button
                @click="checkVerificationStatus"
                :disabled="isChecking"
                class="text-sm font-medium text-yellow-800 hover:text-yellow-900 underline disabled:opacity-50"
              >
                {{ isChecking ? 'Checking...' : 'I just verified, refresh' }}
              </button>
            </div>
          </div>
        </div>
        <button
          @click="dismissBanner"
          class="text-yellow-700 hover:text-yellow-900 ml-4 flex-shrink-0"
          aria-label="Close banner"
        >
          <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path 
              fill-rule="evenodd" 
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
            />
          </svg>
        </button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useAuthStore } from '@/stores/auth'
  import { auth, sendEmailVerification } from '@/config/firebase'
  
  const authStore = useAuthStore()
  const isDismissed = ref(false)
  const isResending = ref(false)
  const isChecking = ref(false)
  const cooldownActive = ref(false)
  const cooldownSeconds = ref(0)
  
  const isVerified = computed(() => authStore.user?.email_verified)
  const isFirebaseUser = computed(() => authStore.user?.auth_provider !== 'email')
  
  const shouldShowBanner = computed(() => {
    return !isVerified.value && !isDismissed.value && isFirebaseUser.value
  })
  
  const buttonText = computed(() => {
    if (isResending.value) return 'Sending...'
    if (cooldownActive.value) return `Wait ${cooldownSeconds.value}s`
    return 'Resend Verification Email'
  })
  
  const resendVerification = async () => {
    isResending.value = true
    
    try {
      const currentUser = auth.currentUser
      
      if (!currentUser) {
        alert('Error: Not authenticated with Firebase. Please log out and log in again.')
        return
      }
      
      await sendEmailVerification(currentUser)
      alert('✅ Verification email sent! Please check your inbox (and spam folder).')
      
      startCooldown()
    } catch (error) {
      console.error('Error sending verification email:', error)
      
      if (error.code === 'auth/too-many-requests') {
        alert('⚠️ Too many requests. Please wait a few minutes before trying again.')
      } else {
        alert('❌ Error sending email: ' + error.message)
      }
    } finally {
      isResending.value = false
    }
  }
  
  const checkVerificationStatus = async () => {
    isChecking.value = true
    
    try {
      const currentUser = auth.currentUser
      
      if (!currentUser) {
        alert('Error: Not authenticated. Please log out and log in again.')
        return
      }
      
      await currentUser.reload()
      
      if (currentUser.emailVerified) {
        const idToken = await currentUser.getIdToken(true)
        await authStore.firebaseLogin(idToken)
        
        alert('✅ Email verified successfully! Welcome to StudHelper.')
        isDismissed.value = true
      } else {
        alert('⚠️ Email not verified yet. Please check your inbox and click the verification link.')
      }
    } catch (error) {
      console.error('Error checking verification status:', error)
      alert('❌ Error checking status: ' + error.message)
    } finally {
      isChecking.value = false
    }
  }
  
  const dismissBanner = () => {
    isDismissed.value = true
    sessionStorage.setItem('verification_banner_dismissed', 'true')
  }
  
  const startCooldown = () => {
    cooldownActive.value = true
    cooldownSeconds.value = 60
    
    const interval = setInterval(() => {
      cooldownSeconds.value--
      
      if (cooldownSeconds.value <= 0) {
        clearInterval(interval)
        cooldownActive.value = false
      }
    }, 1000)
  }
  
  onMounted(() => {
    const wasDismissed = sessionStorage.getItem('verification_banner_dismissed')
    if (wasDismissed) {
      isDismissed.value = true
    }
  })
  </script>
  
  <style scoped>
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .animate-slideDown {
    animation: slideDown 0.4s ease-out;
  }
  </style>