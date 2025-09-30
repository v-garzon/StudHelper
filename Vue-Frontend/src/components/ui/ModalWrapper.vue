<template>
  <teleport to="#modal-container">
    <div v-if="isVisible" class="modal-overlay" @click.self="handleBackdropClick">
      <div class="modal-content">
        <slot />
      </div>
    </div>
  </teleport>
</template>

<script setup>
defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close'])

const handleBackdropClick = () => {
  if (props.closeOnBackdrop) {
    emit('close')
  }
}
</script>

