<template>
  <div class="p-6 space-y-6">
    <div>
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Class Permissions & Access</h3>
      <p class="text-gray-600 mb-6">
        Configure who can access your class and what they can do.
      </p>
    </div>

    <!-- Class Visibility -->
    <div class="space-y-4">
      <h4 class="font-medium text-gray-900">Class Visibility</h4>
      
      <div class="space-y-3">
        <label class="flex items-start space-x-3">
          <input
            v-model="localValue.isPublic"
            type="radio"
            :value="false"
            class="mt-1"
          />
          <div>
            <div class="font-medium text-gray-900">Private Class</div>
            <div class="text-sm text-gray-600">Only invited members can access this class</div>
          </div>
        </label>
        
        <label class="flex items-start space-x-3">
          <input
            v-model="localValue.isPublic"
            type="radio"
            :value="true"
            class="mt-1"
          />
          <div>
            <div class="font-medium text-gray-900">Public Class</div>
            <div class="text-sm text-gray-600">Anyone with the class code can join</div>
          </div>
        </label>
      </div>
    </div>

    <!-- Guest Access -->
    <div class="space-y-4">
      <h4 class="font-medium text-gray-900">Guest Access</h4>
      
      <label class="flex items-center space-x-3">
        <input
          v-model="localValue.allowGuests"
          type="checkbox"
          class="rounded"
        />
        <div>
          <div class="font-medium text-gray-900">Allow guest users</div>
          <div class="text-sm text-gray-600">Let non-registered users participate with limited access</div>
        </div>
      </label>
    </div>

    <!-- Member Limits -->
    <div class="space-y-4">
      <h4 class="font-medium text-gray-900">Member Management</h4>
      
      <div>
        <label for="maxMembers" class="block text-sm font-medium text-gray-700 mb-1">
          Maximum Members
        </label>
        <select
          id="maxMembers"
          v-model="localValue.maxMembers"
          class="input-field"
        >
          <option value="10">10 members</option>
          <option value="25">25 members</option>
          <option value="50">50 members</option>
          <option value="100">100 members</option>
          <option value="unlimited">Unlimited</option>
        </select>
      </div>

      <div>
        <label for="defaultRole" class="block text-sm font-medium text-gray-700 mb-1">
          Default Role for New Members
        </label>
        <select
          id="defaultRole"
          v-model="localValue.defaultRole"
          class="input-field"
        >
          <option value="reader">Reader - Can view and chat only</option>
          <option value="contributor">Contributor - Can upload documents</option>
          <option value="manager">Manager - Can manage class settings</option>
        </select>
      </div>
    </div>

    <!-- Permissions Preview -->
    <div class="bg-gray-50 p-4 rounded-lg">
      <h5 class="font-medium text-gray-900 mb-3">Permission Summary</h5>
      <div class="space-y-2 text-sm">
        <div class="flex items-center space-x-2">
          <div class="w-2 h-2 bg-green-500 rounded-full"></div>
          <span>Class is {{ localValue.isPublic ? 'public' : 'private' }}</span>
        </div>
        <div class="flex items-center space-x-2">
          <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
          <span>{{ localValue.allowGuests ? 'Guests allowed' : 'No guest access' }}</span>
        </div>
        <div class="flex items-center space-x-2">
          <div class="w-2 h-2 bg-purple-500 rounded-full"></div>
          <span>Max {{ localValue.maxMembers }} members</span>
        </div>
        <div class="flex items-center space-x-2">
          <div class="w-2 h-2 bg-orange-500 rounded-full"></div>
          <span>New members join as {{ localValue.defaultRole }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      isPublic: false,
      allowGuests: false,
      maxMembers: 50,
      defaultRole: 'reader'
    })
  },
  errors: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

const localValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
</script>

