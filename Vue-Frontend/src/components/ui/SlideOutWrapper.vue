<template>
  <teleport to="#slideout-container">
    <div v-if="isVisible" class="slideout-overlay">
      <!-- Backdrop -->
      <div 
        class="absolute inset-0 bg-black bg-opacity-25" 
        @click="handleBackdropClick"
      ></div>
      
      <!-- Slide out content -->
      <div :class="[
        'slideout-content',
        isVisible ? 'translate-x-0' : 'translate-x-full'
      ]">
        <slot />
      </div>
    </div>
  </teleport>
</template>

<script setup>
const props = defineProps({
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

