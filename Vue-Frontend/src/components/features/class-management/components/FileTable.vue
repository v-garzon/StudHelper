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
              <input 
                :value="file.description"
                @input="handleDescriptionChange(file, $event.target.value)"
                type="text"
                placeholder="Add description..."
                class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-primary-500 focus:border-transparent"
              />
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
  </div>
</template>

<script setup>
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

function handleDescriptionChange(file, description) {
  emit('description-changed', {
    fileId: file.id,
    description
  })
}

function handleDelete(file) {
  emit('file-removed', file.id)
}
</script>


