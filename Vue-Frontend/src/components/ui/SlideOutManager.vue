<template>
  <div>
    <!-- Render active slide-out -->
    <component
      v-if="activeSlideOut"
      :is="activeSlideOut.name"
      v-bind="activeSlideOut.props"
      @close="closeSlideOut"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useUIStore } from '@/stores/ui'

// Import slide-out components
import ClassInfoPanel from '@/components/features/class-management/panels/ClassInfoPanel.vue'
import UserSettingsPanel from '@/components/features/user-account/panels/UserSettingsPanel.vue'
import QuickUsagePanel from '@/components/features/user-account/panels/QuickUsagePanel.vue'

const uiStore = useUIStore()
const { activeSlideOut } = storeToRefs(uiStore)

const closeSlideOut = () => {
  uiStore.closeSlideOut()
}

// Register slide-out components
const slideOutComponents = {
  ClassInfoPanel,
  UserSettingsPanel,
  QuickUsagePanel
}
</script>

