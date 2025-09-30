import { computed } from 'vue'
import { useClassStore } from '@/stores/classes'

export function useClasses() {
  const classStore = useClassStore()
  
  const classes = computed(() => classStore.classes)
  const currentClass = computed(() => classStore.currentClass)
  const currentChat = computed(() => classStore.currentChat)
  const isLoading = computed(() => classStore.isLoading)
  
  const fetchClasses = async () => {
    return await classStore.fetchClasses()
  }
  
  const createClass = async (classData) => {
    return await classStore.createClass(classData)
  }
  
  const selectClass = (classItem) => {
    classStore.selectClass(classItem)
  }
  
  const selectChat = (chat) => {
    classStore.selectChat(chat)
  }
  
  const joinClass = async (classCode) => {
    return await classStore.joinClass(classCode)
  }
  
  return {
    classes,
    currentClass,
    currentChat,
    isLoading,
    fetchClasses,
    createClass,
    selectClass,
    selectChat,
    joinClass
  }
}

