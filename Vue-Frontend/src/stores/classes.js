import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import classService from '@/services/classService'

export const useClassStore = defineStore('classes', () => {
  // ==========================================
  // STATE
  // ==========================================
  
  const classes = ref([])
  const selectedClass = ref(null)
  const currentChat = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  
  // Upload management
  const uploadQueue = ref([])
  
  // ==========================================
  // GETTERS
  // ==========================================
  
  const hasClasses = computed(() => classes.value.length > 0)
  
  const selectedClassId = computed(() => {
    return selectedClass.value?.id || parseInt(localStorage.getItem('selectedClassId'))
  })
  
  // ==========================================
  // ACTIONS
  // ==========================================
  
  /**
   * Fetch all classes for current user
   */
  async function fetchClasses() {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await classService.getClasses()
      classes.value = response.classes
      
      // Auto-select from localStorage
      const savedId = localStorage.getItem('selectedClassId')
      if (savedId) {
        const savedClass = classes.value.find(c => c.id === parseInt(savedId))
        if (savedClass) {
          selectedClass.value = savedClass
        } else {
          // Clear invalid selection
          localStorage.removeItem('selectedClassId')
        }
      }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      console.error('Failed to fetch classes:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Create new class with files
   */
  async function createClass(classData) {
    isLoading.value = true
    error.value = null
    
    try {
      const formData = new FormData()
      formData.append('name', classData.name)
      formData.append('description', classData.description || '')
      
      // Prepare file descriptions as JSON
      const fileDescriptions = {}
      classData.files.forEach(fileObj => {
        if (fileObj.description) {
          fileDescriptions[fileObj.file.name] = fileObj.description
        }
      })
      
      // Add files
      classData.files.forEach(fileObj => {
        formData.append('files', fileObj.file)
      })
      
      // Add file descriptions as JSON string
      if (Object.keys(fileDescriptions).length > 0) {
        formData.append('file_descriptions', JSON.stringify(fileDescriptions))
      }
      
      // Add YouTube videos
      if (classData.youtubeVideos?.length) {
        const urls = classData.youtubeVideos.map(v => v.url)
        const descriptions = classData.youtubeVideos.map(v => v.description || '')
        
        formData.append('youtube_urls', JSON.stringify(urls))
        formData.append('youtube_descriptions', JSON.stringify(descriptions))
      }
      
      const newClass = await classService.createClass(formData)
      
      // Add to classes list
      classes.value.push(newClass)
      
      // Auto-select new class
      selectClass(newClass)
      
      return newClass
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Fetch detailed class information
   */
  async function fetchClassDetails(classId) {
    isLoading.value = true
    error.value = null
    
    try {
      const classDetails = await classService.getClassDetails(classId)
      
      // Update in list if exists
      const index = classes.value.findIndex(c => c.id === classId)
      if (index !== -1) {
        classes.value[index] = classDetails
      }
      
      // Update selected class if it's the current one
      if (selectedClass.value?.id === classId) {
        selectedClass.value = classDetails
      }
      
      return classDetails
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Update class info
   */
  async function updateClass(classId, updates) {
    isLoading.value = true
    error.value = null
    
    try {
      const updatedClass = await classService.updateClass(classId, updates)
      
      // Update in list
      const index = classes.value.findIndex(c => c.id === classId)
      if (index !== -1) {
        classes.value[index] = { ...classes.value[index], ...updatedClass }
      }
      
      // Update selected if it's the current class
      if (selectedClass.value?.id === classId) {
        selectedClass.value = { ...selectedClass.value, ...updatedClass }
      }
      
      return updatedClass
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Delete class
   */
  async function deleteClass(classId) {
    isLoading.value = true
    error.value = null
    
    try {
      await classService.deleteClass(classId)
      
      // Remove from list
      classes.value = classes.value.filter(c => c.id !== classId)
      
      // Clear selection if deleted class was selected
      if (selectedClass.value?.id === classId) {
        selectedClass.value = null
        localStorage.removeItem('selectedClassId')
      }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Upload document to class
   */
  async function uploadDocument(classId, file, description) {
    try {
      const document = await classService.uploadDocument(classId, file, description)
      
      // Refresh class details to get updated document list
      await fetchClassDetails(classId)
      
      return document
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    }
  }
  
  /**
   * Upload YouTube video to class
   */
  async function uploadYouTubeVideo(classId, url, description) {
    try {
      const document = await classService.uploadYouTubeVideo(classId, url, description)
      
      // Refresh class details
      await fetchClassDetails(classId)
      
      return document
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    }
  }
  
  /**
   * Update document description
   */
  async function updateDocumentDescription(documentId, description) {
    try {
      await classService.updateDocument(documentId, description)
      
      // Refresh current class details if selected
      if (selectedClass.value) {
        await fetchClassDetails(selectedClass.value.id)
      }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    }
  }
  
  /**
   * Delete document
   */
  async function deleteDocument(documentId) {
    try {
      await classService.deleteDocument(documentId)
      
      // Refresh current class details
      if (selectedClass.value) {
        await fetchClassDetails(selectedClass.value.id)
      }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    }
  }
  
  /**
   * Select a class
   */
  function selectClass(classItem) {
    selectedClass.value = classItem
    currentChat.value = null // Clear chat when switching classes
    localStorage.setItem('selectedClassId', classItem.id.toString())
  }
  
  /**
   * Clear class selection
   */
  function clearClassSelection() {
    selectedClass.value = null
    currentChat.value = null
    localStorage.removeItem('selectedClassId')
  }
  
  /**
   * Select a chat (placeholder for Phase 4)
   */
  function selectChat(chat) {
    currentChat.value = chat
  }
  
  /**
   * Add file to upload queue
   */
  function addToUploadQueue(file, description = '') {
    const fileObj = {
      id: Date.now() + Math.random(),
      file,
      description,
      status: 'new', // 'new' | 'modified' | 'deleted'
      isExisting: false
    }
    uploadQueue.value.push(fileObj)
    return fileObj
  }
  
  /**
   * Add existing document to queue (for edit mode)
   */
  function addExistingToQueue(document) {
    const fileObj = {
      id: document.id,
      filename: document.filename,
      file_size: document.file_size,
      file_type: document.file_type,
      description: document.description || '',
      url: document.url,
      status: 'existing',
      isExisting: true,
      originalDescription: document.description || ''
    }
    uploadQueue.value.push(fileObj)
    return fileObj
  }
  
  /**
   * Remove file from upload queue
   */
  function removeFromUploadQueue(fileId) {
    const file = uploadQueue.value.find(f => f.id === fileId)
    
    if (file?.isExisting) {
      // Mark existing file as deleted
      file.status = 'deleted'
    } else {
      // Remove new file completely
      uploadQueue.value = uploadQueue.value.filter(f => f.id !== fileId)
    }
  }
  
  /**
   * Update file description in queue
   */
  function updateFileDescription(fileId, description) {
    const file = uploadQueue.value.find(f => f.id === fileId)
    if (file) {
      file.description = description
      
      // Mark as modified if existing file and description changed
      if (file.isExisting && description !== file.originalDescription) {
        file.status = 'modified'
      }
    }
  }
  
  /**
   * Clear upload queue
   */
  function clearUploadQueue() {
    uploadQueue.value = []
  }
  
  return {
    // State
    classes,
    selectedClass,
    currentChat,
    isLoading,
    error,
    uploadQueue,
    
    // Getters
    hasClasses,
    selectedClassId,
    
    // Actions
    fetchClasses,
    createClass,
    fetchClassDetails,
    updateClass,
    deleteClass,
    uploadDocument,
    uploadYouTubeVideo,
    updateDocumentDescription,
    deleteDocument,
    selectClass,
    clearClassSelection,
    selectChat,
    addToUploadQueue,
    addExistingToQueue,
    removeFromUploadQueue,
    updateFileDescription,
    clearUploadQueue
  }
})


