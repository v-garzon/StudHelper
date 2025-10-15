<template>
  <div class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen p-4">
      <!-- Overlay -->
      <div 
        class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        @click="$emit('close')"
      ></div>
      
      <!-- Modal Content -->
      <div class="relative z-10 bg-white rounded-lg shadow-xl w-full max-w-2xl">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">
            {{ isEdit ? 'Edit' : 'Add' }} Description
          </h3>
          <p class="text-sm text-gray-600 mt-1 truncate">
            {{ filename }}
          </p>
        </div>

        <!-- Content -->
        <div class="px-6 py-4">
          <textarea
            v-model="localDescription"
            placeholder="Describe this file or video..."
            rows="8"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            autofocus
          ></textarea>
          <p class="text-xs text-gray-500 mt-2">
            {{ localDescription.length }} characters
          </p>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
          <button 
            @click="$emit('close')"
            class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="handleSave"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  filename: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'save'])

const localDescription = ref(props.description)

const isEdit = computed(() => props.description.length > 0)

function handleSave() {
  emit('save', localDescription.value)
  emit('close')
}
</script>

