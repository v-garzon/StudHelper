import { defineStore } from 'pinia'
import { ref } from 'vue'
import { classService } from '@/services/classes/classService'

export const useClassStore = defineStore('classes', () => {
  const classes = ref([])
  const currentClass = ref(null)
  const currentChat = ref(null)
  const isLoading = ref(false)

  const fetchClasses = async () => {
    isLoading.value = true
    try {
      const response = await classService.getClasses()
      classes.value = response.data
    } catch (error) {
      console.error('Failed to fetch classes:', error)
    } finally {
      isLoading.value = false
    }
  }

  const selectClass = (classItem) => {
    currentClass.value = classItem
    currentChat.value = null
  }

  const selectChat = (chat) => {
    currentChat.value = chat
  }

  const createClass = async (classData) => {
    try {
      const response = await classService.createClass(classData)
      classes.value.push(response.data)
      return { success: true, data: response.data }
    } catch (error) {
      return { success: false, message: error.response?.data?.message || 'Failed to create class' }
    }
  }

  return {
    classes,
    currentClass,
    currentChat,
    isLoading,
    fetchClasses,
    selectClass,
    selectChat,
    createClass
  }
})

