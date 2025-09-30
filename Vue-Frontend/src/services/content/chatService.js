import api from '../api'

export const chatService = {
  async getChatSessions(classId) {
    return api.get(`/chat/sessions?class_id=${classId}`)
  },

  async createChatSession(sessionData) {
    return api.post('/chat/sessions', sessionData)
  },

  async getChatMessages(sessionId) {
    return api.get(`/chat/sessions/${sessionId}/messages`)
  },

  async sendMessage(sessionId, messageData) {
    return api.post(`/chat/sessions/${sessionId}/messages`, messageData)
  },

  async deleteSession(sessionId) {
    return api.delete(`/chat/sessions/${sessionId}`)
  }
}

