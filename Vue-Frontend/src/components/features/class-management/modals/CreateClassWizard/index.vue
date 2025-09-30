<template>
  <ModalWrapper :is-visible="true" @close="$emit('close')">
    <div class="flex flex-col h-full max-h-[90vh]">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <div>
          <h2 class="text-2xl font-bold text-gray-900">Create New Class</h2>
          <p class="text-gray-600 mt-1">Step {{ currentStep }} of 3</p>
        </div>
        <button @click="$emit('close')" class="p-2 hover:bg-gray-100 rounded-lg">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Progress Bar -->
      <div class="px-6 py-4 bg-gray-50">
        <div class="flex items-center">
          <div
            v-for="step in 3"
            :key="step"
            class="flex items-center"
          >
            <div
              :class="[
                'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
                step <= currentStep ? 'bg-primary-600 text-white' : 'bg-gray-300 text-gray-600'
              ]"
            >
              {{ step }}
            </div>
            <div
              v-if="step < 3"
              :class="[
                'w-16 h-1 mx-2',
                step < currentStep ? 'bg-primary-600' : 'bg-gray-300'
              ]"
            ></div>
          </div>
        </div>
        <div class="flex justify-between mt-2 text-sm">
          <span :class="currentStep >= 1 ? 'text-primary-600 font-medium' : 'text-gray-500'">
            Knowledge Upload
          </span>
          <span :class="currentStep >= 2 ? 'text-primary-600 font-medium' : 'text-gray-500'">
            Permissions
          </span>
          <span :class="currentStep >= 3 ? 'text-primary-600 font-medium' : 'text-gray-500'">
            Billing Settings
          </span>
        </div>
      </div>

      <!-- Step Content -->
      <div class="flex-1 overflow-y-auto">
        <StepKnowledge
          v-if="currentStep === 1"
          v-model="formData.knowledge"
          :errors="errors.knowledge"
        />
        <StepPermissions
          v-if="currentStep === 2"
          v-model="formData.permissions"
          :errors="errors.permissions"
        />
        <StepBilling
          v-if="currentStep === 3"
          v-model="formData.billing"
          :errors="errors.billing"
        />
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
        <button
          v-if="currentStep > 1"
          @click="previousStep"
          class="btn-secondary"
        >
          Previous
        </button>
        <div v-else></div>

        <div class="flex space-x-3">
          <button @click="$emit('close')" class="btn-secondary">
            Cancel
          </button>
          <button
            v-if="currentStep < 3"
            @click="nextStep"
            :disabled="!canProceed"
            class="btn-primary"
          >
            Next
          </button>
          <button
            v-else
            @click="createClass"
            :disabled="isCreating || !canProceed"
            class="btn-primary"
          >
            <span v-if="isCreating">Creating...</span>
            <span v-else>Create Class</span>
          </button>
        </div>
      </div>
    </div>
  </ModalWrapper>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useClassStore } from '@/stores/classes'
import ModalWrapper from '@/components/ui/ModalWrapper.vue'
import StepKnowledge from './StepKnowledge.vue'
import StepPermissions from './StepPermissions.vue'
import StepBilling from './StepBilling.vue'

const emit = defineEmits(['close'])

const classStore = useClassStore()

const currentStep = ref(1)
const isCreating = ref(false)

const formData = ref({
  knowledge: {
    name: '',
    description: '',
    documents: []
  },
  permissions: {
    isPublic: false,
    allowGuests: false,
    maxMembers: 50,
    defaultRole: 'reader'
  },
  billing: {
    tokenLimit: 1000,
    costCenter: '',
    sponsorshipEnabled: false
  }
})

const errors = ref({
  knowledge: {},
  permissions: {},
  billing: {}
})

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 1:
      return formData.value.knowledge.name.trim().length > 0
    case 2:
      return true // Permissions have defaults
    case 3:
      return formData.value.billing.tokenLimit > 0
    default:
      return false
  }
})

const nextStep = () => {
  if (canProceed.value && currentStep.value < 3) {
    currentStep.value++
  }
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const createClass = async () => {
  isCreating.value = true
  
  try {
    const classData = {
      name: formData.value.knowledge.name,
      description: formData.value.knowledge.description,
      // Add other fields as needed for your API
    }
    
    const result = await classStore.createClass(classData)
    
    if (result.success) {
      emit('close')
    } else {
      // Handle error
      console.error('Failed to create class:', result.message)
    }
  } catch (error) {
    console.error('Error creating class:', error)
  } finally {
    isCreating.value = false
  }
}
</script>

