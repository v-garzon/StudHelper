<template>
  <div class="youtube-input">
    <div class="flex items-center space-x-2">
      <div class="flex-1">
        <input
          v-model="youtubeUrl"
          type="url"
          placeholder="Paste YouTube URL here..."
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
          @keyup.enter="handleAddVideo"
        />
      </div>
      <button
        @click="handleAddVideo"
        type="button"
        :disabled="!isValidUrl"
        class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
      >
        Add Video
      </button>
    </div>
    <p v-if="error" class="mt-1 text-sm text-red-600">
      {{ error }}
    </p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['video-added'])

const youtubeUrl = ref('')
const error = ref('')

const isValidUrl = computed(() => {
  if (!youtubeUrl.value) return false
  
  const url = youtubeUrl.value.toLowerCase()
  return url.includes('youtube.com/watch') || 
         url.includes('youtu.be/') || 
         url.includes('youtube.com/embed/')
})

function handleAddVideo() {
  error.value = ''
  
  if (!isValidUrl.value) {
    error.value = 'Please enter a valid YouTube URL'
    return
  }
  
  emit('video-added', {
    url: youtubeUrl.value,
    description: ''
  })
  
  youtubeUrl.value = ''
}
</script>


