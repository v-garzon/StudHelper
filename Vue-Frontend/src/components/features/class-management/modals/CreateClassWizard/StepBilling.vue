<template>
  <div class="p-6 space-y-6">
    <div>
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Usage Limits & Billing</h3>
      <p class="text-gray-600 mb-6">
        Set AI usage limits and configure billing settings for this class.
      </p>
    </div>

    <!-- Token Limits -->
    <div class="space-y-4">
      <h4 class="font-medium text-gray-900">AI Usage Limits</h4>
      
      <div>
        <label for="tokenLimit" class="block text-sm font-medium text-gray-700 mb-1">
          Daily Token Limit per User
        </label>
        <select
          id="tokenLimit"
          v-model="localValue.tokenLimit"
          class="input-field"
        >
          <option value="500">500 tokens (Basic)</option>
          <option value="1000">1,000 tokens (Standard)</option>
          <option value="2500">2,500 tokens (Advanced)</option>
          <option value="5000">5,000 tokens (Premium)</option>
          <option value="unlimited">Unlimited</option>
        </select>
        <p class="text-sm text-gray-600 mt-1">
          Approximately {{ Math.round(localValue.tokenLimit / 4) }} words of AI responses per day
        </p>
      </div>
    </div>

    <!-- Cost Management -->
    <div class="space-y-4">
      <h4 class="font-medium text-gray-900">Cost Management</h4>
      
      <div>
        <label for="costCenter" class="block text-sm font-medium text-gray-700 mb-1">
          Cost Center (optional)
        </label>
        <input
          id="costCenter"
          v-model="localValue.costCenter"
          type="text"
          class="input-field"
          placeholder="Department or project code for billing"
        />
      </div>

      <div class="space-y-3">
        <label class="flex items-start space-x-3">
          <input
            v-model="localValue.sponsorshipEnabled"
            type="checkbox"
            class="mt-1 rounded"
          />
          <div>
            <div class="font-medium text-gray-900">Enable User Sponsorship</div>
            <div class="text-sm text-gray-600">
              Allow class managers to sponsor other users' AI usage
            </div>
          </div>
        </label>
      </div>
    </div>

    <!-- Usage Monitoring -->
    <div class="space-y-4">
      <h4 class="font-medium text-gray-900">Monitoring & Alerts</h4>
      
      <div class="space-y-3">
        <label class="flex items-center space-x-3">
          <input
            v-model="localValue.usageAlerts"
            type="checkbox"
            class="rounded"
          />
          <span class="text-gray-900">Send usage alerts at 80% of limit</span>
        </label>
        
        <label class="flex items-center space-x-3">
          <input
            v-model="localValue.weeklyReports"
            type="checkbox"
            class="rounded"
          />
          <span class="text-gray-900">Weekly usage reports</span>
        </label>
      </div>
    </div>

    <!-- Billing Summary -->
    <div class="bg-blue-50 p-4 rounded-lg">
      <h5 class="font-medium text-gray-900 mb-3">Estimated Costs</h5>
      <div class="space-y-2 text-sm">
        <div class="flex justify-between">
          <span>Daily cost per user ({{ localValue.tokenLimit }} tokens):</span>
          <span class="font-medium">${{ (localValue.tokenLimit * 0.0001).toFixed(3) }}</span>
        </div>
        <div class="flex justify-between">
          <span>Monthly cost per user:</span>
          <span class="font-medium">${{ (localValue.tokenLimit * 0.0001 * 30).toFixed(2) }}</span>
        </div>
        <div class="border-t border-blue-200 pt-2 mt-2">
          <div class="flex justify-between font-medium">
            <span>Estimated monthly cost (10 active users):</span>
            <span>${{ (localValue.tokenLimit * 0.0001 * 30 * 10).toFixed(2) }}</span>
          </div>
        </div>
      </div>
      <p class="text-xs text-gray-600 mt-2">
        Actual costs may vary based on usage patterns and AI model pricing.
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      tokenLimit: 1000,
      costCenter: '',
      sponsorshipEnabled: false,
      usageAlerts: true,
      weeklyReports: false
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

