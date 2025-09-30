<template>
  <div class="h-full flex flex-col">
    <!-- Chat Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="font-semibold text-gray-900">{{ currentChat.title || 'New Chat' }}</h3>
          <p class="text-sm text-gray-600">{{ currentClass.name }}</p>
        </div>
        <div class="flex space-x-2">
          <button class="p-2 rounded-lg hover:bg-gray-100" title="Upload document for this chat">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
            </svg>
          </button>
          <button class="p-2 rounded-lg hover:bg-gray-100" title="Chat settings">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Messages Area -->
    <div class="flex-1 overflow-y-auto p-6 space-y-4">
      <div v-if="messages.length === 0" class="text-center text-gray-500 mt-12">
        <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
        </svg>
        <p>Start a conversation with your AI tutor</p>
        <p class="text-sm mt-1">Ask questions about your uploaded materials</p>
      </div>

      <div
        v-for="message in messages"
        :key="message.id"
        :class="[
          'flex',
          message.is_user ? 'justify-end' : 'justify-start'
        ]"
      >
        <div
          :class="[
            'max-w-[70%] rounded-lg px-4 py-2',
            message.is_user 
              ? 'bg-primary-600 text-white' 
              : 'bg-white border border-gray-200'
          ]"
        >
          <p class="whitespace-pre-wrap">{{ message.content }}</p>
          <p class="text-xs mt-1 opacity-70">
            {{ formatTime(message.timestamp) }}
          </p>
        </div>
      </div>

      <div v-if="isTyping" class="flex justify-start">
        <div class="bg-white border border-gray-200 rounded-lg px-4 py-2">
          <div class="flex space-x-1">
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s;"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s;"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Message Input -->
    <div class="bg-white border-t border-gray-200 p-4">
      <div class="flex space-x-4">
        <div class="flex-1">
          <textarea
            v-model="newMessage"
            @keydown.enter.prevent="handleSendMessage"
            placeholder="Type your message here..."
            class="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            rows="3"
          ></textarea>
        </div>
        <div class="flex flex-col space-y-2">
          <button
            @click="handleSendMessage"
            :disabled="!newMessage.trim() || isTyping"
            class="btn-primary px-6 py-2"
          >
            Send
          </button>
          <button
            @click="attachFile"
            class="btn-secondary px-6 py-2"
          >
            Attach
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useClassStore } from '@/stores/classes'

const classStore = useClassStore()
const { currentClass, currentChat } = storeToRefs(classStore)

const messages = ref([])
const newMessage = ref('')
const isTyping = ref(false)

const handleSendMessage = async () => {
  if (!newMessage.value.trim()) return

  const userMessage = {
    id: Date.now(),
    content: newMessage.value,
    is_user: true,
    timestamp: new Date().toISOString()
  }

  messages.value.push(userMessage)
  const messageContent = newMessage.value
  newMessage.value = ''

  // Show typing indicator
  isTyping.value = true

  // Simulate AI response (replace with actual API call)
  setTimeout(() => {
    const aiResponse = {
      id: Date.now() + 1,
      content: `This is a mock AI response to: "${messageContent}"\n\nI would analyze your uploaded documents and provide a contextual response based on the content.`,
      is_user: false,
      timestamp: new Date().toISOString()
    }
    
    messages.value.push(aiResponse)
    isTyping.value = false
  }, 2000)
}

const attachFile = () => {
  console.log('Open file upload modal for chat-specific documents')
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

onMounted(() => {
  // Load existing messages for this chat
  // This would come from your API
})
</script>

