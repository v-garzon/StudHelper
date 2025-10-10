<template>
  <div class="delete-section border-t border-red-200 pt-6 mt-6">
    <h3 class="text-lg font-medium text-red-900 mb-2">Danger Zone</h3>
    <p class="text-sm text-gray-600 mb-4">
      Once you delete a class, there is no going back. All documents, chat sessions, and member data will be permanently deleted.
    </p>
    <button
      @click="handleDelete"
      :disabled="isDeleting"
      class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
    >
      {{ isDeleting ? 'Deleting...' : 'Delete This Class' }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  className: {
    type: String,
    required: true
  },
  isDeleting: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['delete'])

function handleDelete() {
  emit('delete')
}
</script>


