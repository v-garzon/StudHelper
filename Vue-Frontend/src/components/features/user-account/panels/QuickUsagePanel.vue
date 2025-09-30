<template>
  <SlideOutWrapper :is-visible="true" @close="$emit('close')">
    <div class="h-full flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 class="text-xl font-semibold text-gray-900">Usage Overview</h2>
        <div class="flex items-center space-x-2">
          <router-link
            to="/usage-analytics"
            class="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            Detailed View
          </router-link>
          <button @click="$emit('close')" class="p-2 hover:bg-gray-100 rounded-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">
        <!-- Current Usage -->
        <div>
          <h3 class="font-medium text-gray-900 mb-4">Today's Usage</h3>
          
          <!-- Daily Limit Progress -->
          <div class="bg-gray-50 p-4 rounded-lg">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700">AI Tokens Used</span>
              <span class="text-sm text-gray-600">{{ usageData.daily.used }} / {{ usageData.daily.limit }}</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-primary-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${Math.min((usageData.daily.used / usageData.daily.limit) * 100, 100)}%` }"
              ></div>
            </div>
            <p class="text-xs text-gray-600 mt-2">
              {{ usageData.daily.limit - usageData.daily.used }} tokens remaining today
            </p>
          </div>

          <div class="grid grid-cols-2 gap-4 mt-4">
            <div class="bg-blue-50 p-3 rounded-lg">
              <div class="text-lg font-semibold text-blue-900">{{ usageData.daily.chats }}</div>
              <div class="text-sm text-blue-700">Chat Sessions</div>
            </div>
            <div class="bg-green-50 p-3 rounded-lg">
              <div class="text-lg font-semibold text-green-900">{{ usageData.daily.messages }}</div>
              <div class="text-sm text-green-700">Messages Sent</div>
            </div>
          </div>
        </div>

        <!-- Weekly Overview -->
        <div>
          <h3 class="font-medium text-gray-900 mb-4">This Week</h3>
          
          <div class="bg-gray-50 p-4 rounded-lg">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700">Weekly Usage</span>
              <span class="text-sm text-gray-600">{{ usageData.weekly.used }} / {{ usageData.weekly.limit }}</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-orange-500 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${Math.min((usageData.weekly.used / usageData.weekly.limit) * 100, 100)}%` }"
              ></div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 mt-4">
            <div class="bg-purple-50 p-3 rounded-lg">
              <div class="text-lg font-semibold text-purple-900">${{ usageData.weekly.cost.toFixed(2) }}</div>
              <div class="text-sm text-purple-700">Estimated Cost</div>
            </div>
            <div class="bg-indigo-50 p-3 rounded-lg">
              <div class="text-lg font-semibold text-indigo-900">{{ usageData.weekly.avgDaily }}</div>
              <div class="text-sm text-indigo-700">Avg Daily Usage</div>
            </div>
          </div>
        </div>

        <!-- Usage by Class -->
        <div>
          <h3 class="font-medium text-gray-900 mb-4">Usage by Class</h3>
          
          <div class="space-y-3">
            <div
              v-for="classUsage in usageData.byClass"
              :key="classUsage.id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div>
                <div class="font-medium text-gray-900">{{ classUsage.name }}</div>
                <div class="text-sm text-gray-600">{{ classUsage.messages }} messages</div>
              </div>
              <div class="text-right">
                <div class="font-medium text-gray-900">{{ classUsage.tokens }}</div>
                <div class="text-sm text-gray-600">tokens</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div>
          <h3 class="font-medium text-gray-900 mb-4">Quick Actions</h3>
          
          <div class="space-y-2">
            <button class="w-full flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50">
              <div class="flex items-center space-x-3">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
                <span class="text-gray-900">View Detailed Analytics</span>
              </div>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </button>
            
            <button class="w-full flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50">
              <div class="flex items-center space-x-3">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span class="text-gray-900">Usage History</span>
              </div>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </button>
            
            <button class="w-full flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50">
              <div class="flex items-center space-x-3">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                <span class="text-gray-900">Manage Limits</span>
              </div>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- Alerts -->
        <div v-if="usageData.alerts.length > 0">
          <h3 class="font-medium text-gray-900 mb-4">Alerts</h3>
          
          <div class="space-y-2">
            <div
              v-for="alert in usageData.alerts"
              :key="alert.id"
              :class="[
                'p-3 rounded-lg',
                alert.type === 'warning' ? 'bg-yellow-50 border border-yellow-200' : 'bg-red-50 border border-red-200'
              ]"
            >
              <div class="flex items-start space-x-2">
                <svg 
                  :class="[
                    'w-5 h-5 mt-0.5',
                    alert.type === 'warning' ? 'text-yellow-600' : 'text-red-600'
                  ]"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.996-.833-2.732 0L3.732 16.5c-.77.833.19 2.5 1.732 2.5z"></path>
                </svg>
                <div>
                  <p :class="alert.type === 'warning' ? 'text-yellow-800' : 'text-red-800'" class="font-medium text-sm">
                    {{ alert.title }}
                  </p>
                  <p :class="alert.type === 'warning' ? 'text-yellow-700' : 'text-red-700'" class="text-sm">
                    {{ alert.message }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </SlideOutWrapper>
</template>

<script setup>
import { ref } from 'vue'
import SlideOutWrapper from '@/components/ui/SlideOutWrapper.vue'

const emit = defineEmits(['close'])

// Mock usage data - replace with real API calls
const usageData = ref({
  daily: {
    used: 750,
    limit: 1000,
    chats: 8,
    messages: 24
  },
  weekly: {
    used: 4200,
    limit: 7000,
    cost: 0.84,
    avgDaily: 600
  },
  byClass: [
    { id: 1, name: 'Biology 101', messages: 12, tokens: 320 },
    { id: 2, name: 'Spanish Literature', messages: 8, tokens: 280 },
    { id: 3, name: 'Data Science', messages: 4, tokens: 150 }
  ],
  alerts: [
    {
      id: 1,
      type: 'warning',
      title: 'High Usage Alert',
      message: 'You have used 75% of your daily token limit.'
    }
  ]
})
</script>

