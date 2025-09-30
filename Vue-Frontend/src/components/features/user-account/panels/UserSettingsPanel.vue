<template>
  <SlideOutWrapper :is-visible="true" @close="$emit('close')">
    <div class="h-full flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 class="text-xl font-semibold text-gray-900">User Settings</h2>
        <button @click="$emit('close')" class="p-2 hover:bg-gray-100 rounded-lg">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">
        <!-- Profile Information -->
        <div>
          <h3 class="font-medium text-gray-900 mb-4">Profile Information</h3>
          <div class="space-y-4">
            <div>
              <label for="fullName" class="block text-sm font-medium text-gray-700 mb-1">
                Full Name
              </label>
              <input
                id="fullName"
                v-model="profile.fullName"
                type="text"
                class="input-field"
              />
            </div>
            
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                id="email"
                v-model="profile.email"
                type="email"
                class="input-field"
                disabled
              />
              <p class="text-sm text-gray-500 mt-1">Email cannot be changed</p>
            </div>
            
            <div>
              <label for="username" class="block text-sm font-medium text-gray-700 mb-1">
                Username
              </label>
              <input
                id="username"
                v-model="profile.username"
                type="text"
                class="input-field"
              />
            </div>
          </div>
        </div>

        <!-- Preferences -->
        <div>
          <h3 class="font-medium text-gray-900 mb-4">Preferences</h3>
          <div class="space-y-4">
            <div>
              <label for="language" class="block text-sm font-medium text-gray-700 mb-1">
                Language
              </label>
              <select
                id="language"
                v-model="preferences.language"
                class="input-field"
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
              </select>
            </div>
            
            <div>
              <label for="timezone" class="block text-sm font-medium text-gray-700 mb-1">
                Timezone
              </label>
              <select
                id="timezone"
                v-model="preferences.timezone"
                class="input-field"
              >
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time</option>
                <option value="America/Chicago">Central Time</option>
                <option value="America/Denver">Mountain Time</option>
                <option value="America/Los_Angeles">Pacific Time</option>
                <option value="Europe/Madrid">Madrid Time</option>
              </select>
            </div>
            
            <div>
              <label for="theme" class="block text-sm font-medium text-gray-700 mb-1">
                Theme
              </label>
              <select
                id="theme"
                v-model="preferences.theme"
                class="input-field"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="auto">Auto (System)</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Notifications -->
        <div>
          <h3 class="font-medium text-gray-900 mb-4">Notifications</h3>
          <div class="space-y-3">
            <label class="flex items-center space-x-3">
              <input
                v-model="notifications.emailUpdates"
                type="checkbox"
                class="rounded"
              />
              <span class="text-gray-900">Email updates</span>
            </label>
            
            <label class="flex items-center space-x-3">
              <input
                v-model="notifications.usageAlerts"
                type="checkbox"
                class="rounded"
              />
              <span class="text-gray-900">Usage limit alerts</span>
            </label>
            
            <label class="flex items-center space-x-3">
              <input
                v-model="notifications.weeklyReports"
                type="checkbox"
                class="rounded"
              />
              <span class="text-gray-900">Weekly activity reports</span>
            </label>
            
            <label class="flex items-center space-x-3">
              <input
                v-model="notifications.newFeatures"
                type="checkbox"
                class="rounded"
              />
              <span class="text-gray-900">New feature announcements</span>
            </label>
          </div>
        </div>

        <!-- AI Preferences -->
        <div>
          <h3 class="font-medium text-gray-900 mb-4">AI Assistant Preferences</h3>
          <div class="space-y-4">
            <div>
              <label for="responseStyle" class="block text-sm font-medium text-gray-700 mb-1">
                Response Style
              </label>
              <select
                id="responseStyle"
                v-model="aiPreferences.responseStyle"
                class="input-field"
              >
                <option value="concise">Concise</option>
                <option value="detailed">Detailed</option>
                <option value="balanced">Balanced</option>
              </select>
            </div>
            
            <div>
              <label for="academicLevel" class="block text-sm font-medium text-gray-700 mb-1">
                Academic Level
              </label>
              <select
                id="academicLevel"
                v-model="aiPreferences.academicLevel"
                class="input-field"
              >
                <option value="high-school">High School</option>
                <option value="undergraduate">Undergraduate</option>
                <option value="graduate">Graduate</option>
                <option value="professional">Professional</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Data & Privacy -->
        <div>
          <h3 class="font-medium text-gray-900 mb-4">Data & Privacy</h3>
          <div class="space-y-3">
            <label class="flex items-center space-x-3">
              <input
                v-model="privacy.improveService"
                type="checkbox"
                class="rounded"
              />
              <span class="text-gray-900">Help improve service with usage data</span>
            </label>
            
            <label class="flex items-center space-x-3">
              <input
                v-model="privacy.shareAnonymous"
                type="checkbox"
                class="rounded"
              />
              <span class="text-gray-900">Share anonymous analytics</span>
            </label>
          </div>
          
          <div class="mt-6 pt-6 border-t border-gray-200">
            <button class="text-red-600 hover:text-red-800 text-sm font-medium">
              Download My Data
            </button>
            <br>
            <button class="text-red-600 hover:text-red-800 text-sm font-medium mt-2">
              Delete Account
            </button>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="border-t border-gray-200 p-6">
        <div class="flex justify-end space-x-3">
          <button @click="$emit('close')" class="btn-secondary">
            Cancel
          </button>
          <button @click="saveSettings" class="btn-primary">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  </SlideOutWrapper>
</template>

<script setup>
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import SlideOutWrapper from '@/components/ui/SlideOutWrapper.vue'

const emit = defineEmits(['close'])

const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

// Form data
const profile = ref({
  fullName: user.value?.full_name || '',
  email: user.value?.email || '',
  username: user.value?.username || ''
})

const preferences = ref({
  language: 'en',
  timezone: 'UTC',
  theme: 'light'
})

const notifications = ref({
  emailUpdates: true,
  usageAlerts: true,
  weeklyReports: false,
  newFeatures: true
})

const aiPreferences = ref({
  responseStyle: 'balanced',
  academicLevel: 'undergraduate'
})

const privacy = ref({
  improveService: true,
  shareAnonymous: false
})

const saveSettings = async () => {
  try {
    // Here you would call your API to save settings
    console.log('Saving settings...', {
      profile: profile.value,
      preferences: preferences.value,
      notifications: notifications.value,
      aiPreferences: aiPreferences.value,
      privacy: privacy.value
    })
    
    // Show success message
    emit('close')
  } catch (error) {
    console.error('Failed to save settings:', error)
  }
}
</script>

