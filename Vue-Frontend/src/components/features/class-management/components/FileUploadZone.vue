<template>
  <div class="file-upload-zone space-y-3">
    <!-- Drag & Drop Area -->
    <div 
      class="drop-zone border-2 border-dashed rounded-lg p-8 text-center transition-colors"
      :class="{
        'border-primary-400 bg-primary-50': isDragging,
        'border-gray-300 hover:border-gray-400': !isDragging
      }"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @drop.prevent="handleDrop"
    >
      <div class="drop-content">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
        </svg>
        <p class="mt-2 text-sm text-gray-600">
          Drag files here or
        </p>
        <button 
          @click="triggerFileInput"
          type="button"
          class="mt-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Browse Files
        </button>
        <p class="mt-2 text-xs text-gray-500">
          PDF, DOCX, XLSX, PPTX, TXT (Max 10MB)
        </p>
      </div>
      <input 
        ref="fileInput"
        type="file"
        multiple
        accept=".pdf,.docx,.xlsx,.pptx,.txt"
        @change="handleFileSelect"
        class="hidden"
      />
    </div>

    <!-- YouTube Input -->
    <YouTubeInput @video-added="handleYouTubeVideo" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import YouTubeInput from './YouTubeInput.vue'

const emit = defineEmits(['file-added', 'youtube-added'])

const fileInput = ref(null)
const isDragging = ref(false)

function triggerFileInput() {
  fileInput.value?.click()
}

function handleDrop(event) {
  isDragging.value = false
  const files = Array.from(event.dataTransfer.files)
  processFiles(files)
}

function handleFileSelect(event) {
  const files = Array.from(event.target.files)
  processFiles(files)
  // Reset input
  event.target.value = ''
}

function processFiles(files) {
  files.forEach(file => {
    if (validateFile(file)) {
      emit('file-added', {
        file,
        description: ''
      })
    } else {
      alert(`Invalid file: ${file.name}. Please check file type and size.`)
    }
  })
}

function validateFile(file) {
  // Check file size (10MB limit)
  if (file.size > 10 * 1024 * 1024) {
    return false
  }
  
  // Check file type
  const allowedTypes = ['pdf', 'docx', 'xlsx', 'pptx', 'txt']
  const ext = file.name.split('.').pop().toLowerCase()
  return allowedTypes.includes(ext)
}

function handleYouTubeVideo(videoData) {
  emit('youtube-added', videoData)
}
</script>


