<template>
  <div class="p-6 space-y-6">
    <div>
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Class Information & Knowledge Base</h3>
      <p class="text-gray-600 mb-6">
        Set up your class details and upload initial study materials.
      </p>
    </div>

    <!-- Basic Information -->
    <div class="space-y-4">
      <div>
        <label for="className" class="block text-sm font-medium text-gray-700 mb-1">
          Class Name *
        </label>
        <input
          id="className"
          v-model="localValue.name"
          type="text"
          required
          class="input-field"
          placeholder="e.g., Biology 101, Spanish Literature"
        />
        <p v-if="errors.name" class="text-red-600 text-sm mt-1">{{ errors.name }}</p>
      </div>

      <div>
        <label for="classDescription" class="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          id="classDescription"
          v-model="localValue.description"
          rows="3"
          class="input-field"
          placeholder="Brief description of what this class covers..."
        ></textarea>
      </div>
    </div>

    <!-- Document Upload -->
    <div>
      <h4 class="font-medium text-gray-900 mb-3">Initial Study Materials</h4>
      <p class="text-sm text-gray-600 mb-4">
        Upload documents to create your knowledge base. You can add more later.
      </p>
      
      <div class="border-2 border-dashed border-gray-300 rounded-lg p-8">
        <div class="text-center">
          <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <div class="mt-4">
            <label for="file-upload" class="cursor-pointer">
              <span class="mt-2 block text-sm font-medium text-gray-900">
                Upload files or drag and drop
              </span>
              <span class="mt-1 block text-sm text-gray-600">
                PDF, DOC, DOCX, PPT, PPTX up to 10MB each
              </span>
              <input id="file-upload" name="file-upload" type="file" class="sr-only" multiple accept=".pdf,.doc,.docx,.ppt,.pptx" @change="handleFileUpload">
            </label>
          </div>
        </div>
      </div>

      <!-- Uploaded Files List -->
      <div v-if="localValue.documents.length > 0" class="mt-4 space-y-2">
        <h5 class="font-medium text-gray-900">Uploaded Files:</h5>
        <div
          v-for="(file, index) in localValue.documents"
          :key="index"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div class="flex items-center space-x-3">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <span class="text-sm text-gray-900">{{ file.name }}</span>
            <span class="text-xs text-gray-500">({{ formatFileSize(file.size) }})</span>
          </div>
          <button
            @click="removeFile(index)"
            class="text-red-600 hover:text-red-800"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- YouTube URL -->
      <div class="mt-6">
        <label for="youtubeUrl" class="block text-sm font-medium text-gray-700 mb-1">
          YouTube Video URL (optional)
        </label>
        <input
          id="youtubeUrl"
          v-model="youtubeUrl"
          type="url"
          class="input-field"
          placeholder="https://www.youtube.com/watch?v=..."
        />
        <button
          v-if="youtubeUrl"
          @click="addYouTubeVideo"
          class="mt-2 btn-secondary text-sm"
        >
          Add Video
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      name: '',
      description: '',
      documents: []
    })
  },
  errors: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

const youtubeUrl = ref('')

const localValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const handleFileUpload = (event) => {
  const files = Array.from(event.target.files)
  localValue.value = {
    ...localValue.value,
    documents: [...localValue.value.documents, ...files]
  }
}

const removeFile = (index) => {
  const documents = [...localValue.value.documents]
  documents.splice(index, 1)
  localValue.value = {
    ...localValue.value,
    documents
  }
}

const addYouTubeVideo = () => {
  if (youtubeUrl.value) {
    const videoData = {
      name: `YouTube Video: ${youtubeUrl.value}`,
      type: 'youtube',
      url: youtubeUrl.value,
      size: 0
    }
    localValue.value = {
      ...localValue.value,
      documents: [...localValue.value.documents, videoData]
    }
    youtubeUrl.value = ''
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

