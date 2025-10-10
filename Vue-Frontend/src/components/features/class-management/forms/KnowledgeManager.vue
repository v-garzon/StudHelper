<template>
  <div class="knowledge-manager space-y-4">
    <h3 class="text-lg font-medium text-gray-900">Knowledge Base</h3>
    
    <!-- Upload Zone -->
    <FileUploadZone 
      @file-added="handleFileAdded"
      @youtube-added="handleYouTubeAdded"
    />

    <!-- File Table -->
    <FileTable 
      v-if="files.length > 0"
      :files="files"
      :mode="mode"
      @description-changed="handleDescriptionChanged"
      @file-removed="handleFileRemoved"
    />

    <p v-else class="text-sm text-gray-500 text-center py-4">
      No files uploaded yet. Add files or YouTube videos to get started.
    </p>
  </div>
</template>

<script setup>
import FileUploadZone from '../components/FileUploadZone.vue'
import FileTable from '../components/FileTable.vue'

const props = defineProps({
  files: {
    type: Array,
    required: true
  },
  mode: {
    type: String,
    default: 'create'
  }
})

const emit = defineEmits(['file-added', 'file-removed', 'description-changed', 'youtube-added'])

function handleFileAdded(fileObj) {
  emit('file-added', fileObj)
}

function handleFileRemoved(fileId) {
  emit('file-removed', fileId)
}

function handleDescriptionChanged(data) {
  emit('description-changed', data)
}

function handleYouTubeAdded(videoData) {
  emit('youtube-added', videoData)
}
</script>


