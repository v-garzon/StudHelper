<template>
  <div>
    <!-- Render active modal -->
    <component
      v-if="activeModal"
      :is="activeModal.name"
      v-bind="activeModal.props"
      @close="closeModal"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useUIStore } from '@/stores/ui'

// Import modal components
import CreateClassModal from '@/components/features/class-management/modals/CreateClassWizard/index.vue'

const uiStore = useUIStore()
const { activeModal } = storeToRefs(uiStore)

const closeModal = () => {
  uiStore.closeModal()
}

// Register modal components
const modalComponents = {
  CreateClassModal
}
</script>

