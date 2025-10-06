<template>
  <div class="bg-white p-8 rounded-2xl shadow-lg">
    <h2 class="text-2xl font-bold text-gray-900 mb-6">Create Account</h2>
    
    <!-- OAuth Buttons -->
    <div class="space-y-3 mb-6">
      <button
        @click="handleGoogleSignup"
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
        @click="handleMicrosoftSignup"
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
    <form @submit.prevent="handleEmailSubmit" class="space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
            Name
          </label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            required
            class="input-field"
            placeholder="First name"
          />
        </div>

        <div>
          <label for="surname" class="block text-sm font-medium text-gray-700 mb-1">
            Surname
          </label>
          <input
            id="surname"
            v-model="form.surname"
            type="text"
            required
            class="input-field"
            placeholder="Last name"
          />
        </div>
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
          @blur="validateEmail"
        />
        <p v-if="emailError" class="text-red-600 text-xs mt-1">
          {{ emailError }}
        </p>
      </div>

      <div>
        <label for="alias" class="block text-sm font-medium text-gray-700 mb-1">
          Alias <span class="text-gray-500 text-xs">(optional)</span>
        </label>
        <input
          id="alias"
          v-model="form.alias"
          type="text"
          class="input-field"
          placeholder="How you'd like to be called"
        />
        <p class="text-xs text-gray-500 mt-1">
          If set, this is how you'll be displayed. Otherwise we'll use your full name.
        </p>
      </div>

      <div>
        <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
            Password
        </label>
        <div class="relative">
            <input
            id="password"
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            required
            class="input-field pr-10"
            placeholder="Create a password"
            @input="checkPasswordStrength"
            />
            <button
            type="button"
            @mousedown="showPassword = true"
            @mouseup="showPassword = false"
            @mouseleave="showPassword = false"
            @touchstart="showPassword = true"
            @touchend="showPassword = false"
            class="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-gray-500 hover:text-gray-700 focus:outline-none"
            tabindex="-1"
            >
            <svg 
                v-if="!showPassword" 
                class="w-5 h-5" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
            >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
            </svg>
            <svg 
                v-else 
                class="w-5 h-5" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
            >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path>
            </svg>
            </button>
        </div>
        
        <!-- Password Strength Indicator -->
        <div v-if="form.password" class="mt-2">
          <div class="flex items-center gap-2 mb-1">
            <div class="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div 
                :class="[
                  'h-full transition-all duration-300',
                  passwordStrength.color === 'red' ? 'bg-red-500 w-1/3' : '',
                  passwordStrength.color === 'yellow' ? 'bg-yellow-500 w-2/3' : '',
                  passwordStrength.color === 'green' ? 'bg-green-500 w-full' : ''
                ]"
              ></div>
            </div>
            <span 
              :class="[
                'text-xs font-medium',
                passwordStrength.color === 'red' ? 'text-red-600' : '',
                passwordStrength.color === 'yellow' ? 'text-yellow-600' : '',
                passwordStrength.color === 'green' ? 'text-green-600' : ''
              ]"
            >
              {{ passwordStrength.label }}
            </span>
          </div>
          
          <!-- Password Requirements -->
          <div class="space-y-1 text-xs">
            <div :class="passwordRequirements.minLength ? 'text-green-600' : 'text-gray-500'">
                <span>{{ passwordRequirements.minLength ? '✓' : '○' }}</span>
                At least 6 characters
            </div>
            <div :class="passwordRequirements.hasUppercase ? 'text-green-600' : 'text-gray-500'">
                <span>{{ passwordRequirements.hasUppercase ? '✓' : '○' }}</span>
                At least 1 uppercase letter
            </div>
            <div :class="passwordRequirements.hasNumbers ? 'text-green-600' : 'text-gray-500'">
                <span>{{ passwordRequirements.hasNumbers ? '✓' : '○' }}</span>
                At least 1 number
            </div>
            <div :class="passwordRequirements.hasSpecialChars ? 'text-green-600' : 'text-gray-500'">
                <span>{{ passwordRequirements.hasSpecialChars ? '✓' : '○' }}</span>
                Special character (!@#$%^&*) <span class="text-gray-400">- for strong password</span>
            </div>
          </div>
        </div>
      </div>

      <div>
        <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1">
            Confirm Password
        </label>
        <div class="relative">
            <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            :type="showConfirmPassword ? 'text' : 'password'"
            required
            class="input-field pr-10"
            placeholder="Re-enter your password"
            @input="checkPasswordMatch"
            />
            <button
            type="button"
            @mousedown="showConfirmPassword = true"
            @mouseup="showConfirmPassword = false"
            @mouseleave="showConfirmPassword = false"
            @touchstart="showConfirmPassword = true"
            @touchend="showConfirmPassword = false"
            class="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-gray-500 hover:text-gray-700 focus:outline-none"
            tabindex="-1"
            >
            <svg 
                v-if="!showConfirmPassword" 
                class="w-5 h-5" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
            >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
            </svg>
            <svg 
                v-else 
                class="w-5 h-5" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
            >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path>
            </svg>
            </button>
        </div>
        <p v-if="passwordMatchError && form.confirmPassword" class="text-red-600 text-xs mt-1">
          {{ passwordMatchError }}
        </p>
        <p v-if="!passwordMatchError && form.confirmPassword && form.password === form.confirmPassword" class="text-green-600 text-xs mt-1">
          ✓ Passwords match
        </p>
      </div>

      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-3">
        <p class="text-red-800 text-sm font-medium">{{ error }}</p>
      </div>

      <div v-if="successMessage" class="bg-green-50 border border-green-200 rounded-lg p-3">
        <p class="text-green-800 text-sm font-medium">{{ successMessage }}</p>
      </div>

      <button 
        type="submit" 
        :disabled="isLoading || !isFormValid"
        class="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="isLoading">Creating account...</span>
        <span v-else>Register with Email</span>
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
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { 
  auth, 
  googleProvider, 
  microsoftProvider, 
  signInWithPopup,
  createUserWithEmailAndPassword,
  sendEmailVerification
} from '@/config/firebase'

const emit = defineEmits(['success', 'switch-to-login', 'cancel'])

const authStore = useAuthStore()
const form = ref({
  name: '',
  surname: '',
  email: '',
  alias: '',
  password: '',
  confirmPassword: ''
})
const error = ref('')
const emailError = ref('')
const passwordMatchError = ref('')
const successMessage = ref('')
const isLoading = ref(false)

const showPassword = ref(false)
const showConfirmPassword = ref(false)

const passwordRequirements = ref({
  minLength: false,
  hasUppercase: false,
  hasNumbers: false,
  hasSpecialChars: false  // NEW
})

const passwordStrength = ref({
  color: 'red',
  label: 'Weak'
})

// Email validation
const validateEmail = () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (form.value.email && !emailRegex.test(form.value.email)) {
    emailError.value = 'Please enter a valid email address'
  } else {
    emailError.value = ''
  }
}

// Password strength checker
const checkPasswordStrength = () => {
  const password = form.value.password
  
  // Check requirements
  passwordRequirements.value.minLength = password.length >= 6
  passwordRequirements.value.hasUppercase = /[A-Z]/.test(password)
  passwordRequirements.value.hasNumbers = (password.match(/\d/g) || []).length >= 1  // CHANGED: 3 → 1
  passwordRequirements.value.hasSpecialChars = /[!@#$%^&*(),.?":{}|<>]/.test(password)  // NEW
  
  // Calculate strength
  const meetsBasicRequirements = 
    passwordRequirements.value.minLength && 
    passwordRequirements.value.hasUppercase && 
    passwordRequirements.value.hasNumbers
  
  const isLong = password.length >= 10
  
  if (!meetsBasicRequirements) {
    passwordStrength.value = { color: 'red', label: 'Weak' }
  } else if (passwordRequirements.value.hasSpecialChars && isLong) {
    passwordStrength.value = { color: 'green', label: 'Strong' }
  } else {
    passwordStrength.value = { color: 'yellow', label: 'Medium' }
  }
}

// Password match checker
const checkPasswordMatch = () => {
  if (form.value.confirmPassword && form.value.password !== form.value.confirmPassword) {
    passwordMatchError.value = 'Passwords do not match'
  } else {
    passwordMatchError.value = ''
  }
}

// Form validation
const isFormValid = computed(() => {
  return (
    form.value.name &&
    form.value.surname &&
    form.value.email &&
    !emailError.value &&
    form.value.password &&
    form.value.confirmPassword &&
    form.value.password === form.value.confirmPassword &&
    passwordRequirements.value.minLength &&
    passwordRequirements.value.hasUppercase &&
    passwordRequirements.value.hasNumbers
  )
})

// Email/Password Registration
const handleEmailSubmit = async () => {
  // Final validation
  if (!isFormValid.value) {
    error.value = 'Please fill all required fields correctly'
    return
  }

  isLoading.value = true
  error.value = ''
  successMessage.value = ''
  
  try {
    // Step 1: Create Firebase account
    const userCredential = await createUserWithEmailAndPassword(
      auth, 
      form.value.email, 
      form.value.password
    )
    
    // Step 2: Send verification email
    await sendEmailVerification(userCredential.user)
    successMessage.value = 'Verification email sent! Please check your inbox.'
    
    // Step 3: Get Firebase ID token
    const idToken = await userCredential.user.getIdToken()
    
    // Step 4: Send to backend with name, surname, and alias
    const result = await authStore.firebaseLogin({
      idToken: idToken,
      name: form.value.name,
      surname: form.value.surname,
      alias: form.value.alias || null
    })
    
    if (result.success) {
      emit('success')
    } else {
      error.value = result.message
    }
  } catch (err) {
    console.error('Registration error:', err)
    
    // Detailed error messages
    if (err.code === 'auth/email-already-in-use') {
      // Try to determine OAuth provider
      const provider = await getEmailProvider(form.value.email)
      if (provider) {
        error.value = `This email is already registered with ${provider}. Please sign in using that method.`
      } else {
        error.value = 'This email is already registered. Please login instead or use "Forgot Password" if you need to reset it.'
      }
    } else if (err.code === 'auth/weak-password') {
      error.value = 'Password does not meet requirements. Please ensure it has at least 6 characters, 1 uppercase letter, and 1 number.'
    } else if (err.code === 'auth/invalid-email') {
      error.value = 'Invalid email format. Please check your email address.'
    } else if (err.code === 'auth/operation-not-allowed') {
      error.value = 'Email/password registration is currently disabled. Please contact support.'
    } else if (err.response?.data?.detail) {
      error.value = err.response.data.detail
    } else {
      error.value = 'Registration failed: ' + (err.message || 'Unknown error occurred. Please try again.')
    }
  } finally {
    isLoading.value = false
  }
}

// Helper to get OAuth provider if email exists
const getEmailProvider = async (email) => {
  try {
    const { fetchSignInMethodsForEmail } = await import('firebase/auth')
    const methods = await fetchSignInMethodsForEmail(auth, email)
    if (methods.includes('google.com')) return 'Google'
    if (methods.includes('microsoft.com')) return 'Microsoft'
    return null
  } catch {
    return null
  }
}

// Google OAuth
const handleGoogleSignup = async () => {
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
    console.error('Google signup error:', err)
    if (err.code === 'auth/popup-closed-by-user') {
      error.value = 'Sign-up cancelled. Please try again.'
    } else if (err.code === 'auth/account-exists-with-different-credential') {
      error.value = 'An account already exists with this email using a different sign-in method. Please use that method to login.'
    } else if (err.code === 'auth/popup-blocked') {
      error.value = 'Popup was blocked by your browser. Please allow popups for this site.'
    } else {
      error.value = 'Google sign-up failed: ' + (err.message || 'Unknown error')
    }
  } finally {
    isLoading.value = false
  }
}

// Microsoft OAuth
const handleMicrosoftSignup = async () => {
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
    console.error('Microsoft signup error:', err)
    if (err.code === 'auth/popup-closed-by-user') {
      error.value = 'Sign-up cancelled. Please try again.'
    } else if (err.code === 'auth/account-exists-with-different-credential') {
      error.value = 'An account already exists with this email using a different sign-in method. Please use that method to login.'
    } else if (err.code === 'auth/popup-blocked') {
      error.value = 'Popup was blocked by your browser. Please allow popups for this site.'
    } else {
      error.value = 'Microsoft sign-up failed: ' + (err.message || 'Unknown error')
    }
  } finally {
    isLoading.value = false
  }
}
</script>


