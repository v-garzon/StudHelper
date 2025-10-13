<template>
  <div class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen px-4">
      <!-- Overlay -->
      <div 
        class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        @click="$emit('close')"
      ></div>
      
      <!-- Modal Content -->
      <div class="relative bg-white rounded-lg shadow-xl">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
defineEmits(['close'])

// This prevents props from being passed down
defineOptions({
  inheritAttrs: false
})
</script>