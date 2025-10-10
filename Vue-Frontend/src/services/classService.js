import api from './api'

const classService = {
  /**
   * Create a new class with optional files and YouTube videos
   */
  async createClass(formData) {
    const response = await api.post('/classes', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  /**
   * Get all classes for current user
   */
  async getClasses() {
    const response = await api.get('/classes')
    return response.data
  },

  /**
   * Get detailed information about a class
   */
  async getClassDetails(classId) {
    const response = await api.get(`/classes/${classId}`)
    return response.data
  },

  /**
   * Update class information
   */
  async updateClass(classId, data) {
    const response = await api.put(`/classes/${classId}`, data)
    return response.data
  },

  /**
   * Delete a class
   */
  async deleteClass(classId) {
    await api.delete(`/classes/${classId}`)
  },

  /**
   * Upload document to class
   */
  async uploadDocument(classId, file, description) {
    const formData = new FormData()
    formData.append('file', file)
    if (description) {
      formData.append('description', description)
    }

    const response = await api.post(`/documents/classes/${classId}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  /**
   * Upload YouTube video to class
   */
  async uploadYouTubeVideo(classId, url, description) {
    const response = await api.post(`/documents/classes/${classId}/upload-youtube`, {
      url,
      description
    })
    return response.data
  },

  /**
   * Get documents for a class
   */
  async getClassDocuments(classId) {
    const response = await api.get(`/documents/classes/${classId}`)
    return response.data
  },

  /**
   * Update document description
   */
  async updateDocument(documentId, description) {
    const response = await api.put(`/documents/${documentId}`, {
      description
    })
    return response.data
  },

  /**
   * Delete a document
   */
  async deleteDocument(documentId) {
    await api.delete(`/documents/${documentId}`)
  }
}

export default classService


