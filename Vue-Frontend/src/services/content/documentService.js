import api from '../api'

export const documentService = {
  async uploadClassDocument(classId, file) {
    const formData = new FormData()
    formData.append('file', file)
    
    return api.post(`/documents/classes/${classId}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  async uploadChatDocument(sessionId, file) {
    const formData = new FormData()
    formData.append('file', file)
    
    return api.post(`/documents/sessions/${sessionId}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  async getClassDocuments(classId) {
    return api.get(`/documents/classes/${classId}`)
  },

  async getChatDocuments(sessionId) {
    return api.get(`/documents/sessions/${sessionId}`)
  },

  async deleteDocument(documentId) {
    return api.delete(`/documents/${documentId}`)
  }
}

