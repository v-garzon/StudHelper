import { ref } from 'vue'
import { validateFileUpload } from '@/utils/validators'
import { documentService } from '@/services/content/documentService'

export function useFileUpload() {
  const isUploading = ref(false)
  const uploadProgress = ref(0)
  const uploadError = ref(null)
  
  const uploadClassDocument = async (classId, file) => {
    const validation = validateFileUpload(file)
    if (!validation.isValid) {
      uploadError.value = validation.error
      return { success: false, error: validation.error }
    }
    
    isUploading.value = true
    uploadError.value = null
    uploadProgress.value = 0
    
    try {
      const response = await documentService.uploadClassDocument(classId, file)
      uploadProgress.value = 100
      
      return { success: true, data: response.data }
    } catch (error) {
      uploadError.value = error.response?.data?.message || 'Upload failed'
      return { success: false, error: uploadError.value }
    } finally {
      isUploading.value = false
    }
  }
  
  const uploadChatDocument = async (sessionId, file) => {
    const validation = validateFileUpload(file)
    if (!validation.isValid) {
      uploadError.value = validation.error
      return { success: false, error: validation.error }
    }
    
    isUploading.value = true
    uploadError.value = null
    uploadProgress.value = 0
    
    try {
      const response = await documentService.uploadChatDocument(sessionId, file)
      uploadProgress.value = 100
      
      return { success: true, data: response.data }
    } catch (error) {
      uploadError.value = error.response?.data?.message || 'Upload failed'
      return { success: false, error: uploadError.value }
    } finally {
      isUploading.value = false
    }
  }
  
  const uploadMultipleFiles = async (files, uploadFn) => {
    const results = []
    
    for (const file of files) {
      const result = await uploadFn(file)
      results.push({ file: file.name, ...result })
    }
    
    return results
  }
  
  return {
    isUploading,
    uploadProgress,
    uploadError,
    uploadClassDocument,
    uploadChatDocument,
    uploadMultipleFiles
  }
}

