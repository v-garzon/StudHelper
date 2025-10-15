<template>
  <div class="file-table-container">
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="px-4 py-3 text-left font-medium text-gray-700">Filename</th>
            <th class="px-4 py-3 text-left font-medium text-gray-700">Size</th>
            <th class="px-4 py-3 text-left font-medium text-gray-700">Description</th>
            <th class="px-4 py-3 text-center font-medium text-gray-700">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr 
            v-for="file in files" 
            :key="file.id"
            :class="getRowClass(file)"
            class="transition-colors"
          >
            <td class="px-4 py-3">
              <div class="flex items-center space-x-2">
                <span class="text-xl">{{ getFileIcon(file) }}</span>
                <span class="font-medium text-gray-900 truncate max-w-xs">
                  {{ getFilename(file) }}
                </span>
              </div>
            </td>
            <td class="px-4 py-3 text-gray-600">
              {{ formatFileSize(file) }}
            </td>
            <td class="px-4 py-3">
              <!-- Empty state - Add button -->
              <button
                v-if="!file.description || file.description.trim() === ''"
                @click="openDescriptionModal(file)"
                class="px-3 py-1 text-sm text-primary-600 hover:bg-primary-50 rounded border border-primary-300 transition-colors"
              >
                + Add
              </button>

              <!-- Has description - Preview with hover effect -->
              <div
                v-else
                @click="openDescriptionModal(file)"
                class="relative cursor-pointer group"
              >
                <p class="text-gray-700 truncate group-hover:blur-sm transition-all duration-200">
                  {{ file.description }}
                </p>
                <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <span class="text-sm font-medium text-primary-600">Edit</span>
                </div>
              </div>
            </td>
            <td class="px-4 py-3 text-center">
              <button 
                @click="handleDelete(file)"
                class="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                title="Delete"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Description Editor Modal -->
    <DescriptionEditorModal
      v-if="editingFile"
      :filename="getFilename(editingFile)"
      :description="editingFile.description || ''"
      @close="editingFile = null"
      @save="handleDescriptionSave"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import DescriptionEditorModal from './DescriptionEditorModal.vue'

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

const emit = defineEmits(['description-changed', 'file-removed'])

const editingFile = ref(null)

const FILE_TYPE_ICONS = {
  pdf: '📄',
  docx: '📝',
  xlsx: '📊',
  pptx: '📊',
  txt: '📃',
  youtube: '🎥',
  unknown: '📎'
}

function getRowClass(file) {
  if (file.status === 'new') return 'bg-green-50'
  if (file.status === 'deleted') return 'bg-red-50 opacity-60'
  if (file.status === 'modified') return 'bg-orange-50'
  return 'bg-white hover:bg-gray-50'
}

function getFileIcon(file) {
  const type = file.file_type || (file.isYouTube ? 'youtube' : file.file?.name?.split('.').pop()?.toLowerCase() || 'unknown')
  return FILE_TYPE_ICONS[type] || FILE_TYPE_ICONS.unknown
}

function getFilename(file) {
  if (file.isYouTube) {
    return file.url
  }
  return file.filename || file.file?.name || 'Unknown file'
}

function formatFileSize(file) {
  if (file.isYouTube) {
    return 'Video'
  }
  
  const bytes = file.file_size || file.file?.size || 0
  if (bytes === 0) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function openDescriptionModal(file) {
  editingFile.value = file
}

function handleDescriptionSave(description) {
  if (editingFile.value) {
    emit('description-changed', {
      fileId: editingFile.value.id,
      description
    })
  }
}

function handleDelete(file) {
  emit('file-removed', file.id)
}
</script>

