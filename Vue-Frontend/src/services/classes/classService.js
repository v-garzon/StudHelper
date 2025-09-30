import api from '../api'

export const classService = {
  async getClasses() {
    return api.get('/classes')
  },

  async createClass(classData) {
    return api.post('/classes', classData)
  },

  async getClass(classId) {
    return api.get(`/classes/${classId}`)
  },

  async updateClass(classId, classData) {
    return api.put(`/classes/${classId}`, classData)
  },

  async deleteClass(classId) {
    return api.delete(`/classes/${classId}`)
  },

  async joinClass(classCode) {
    return api.post('/classes/join', { class_code: classCode })
  },

  async getClassMembers(classId) {
    return api.get(`/classes/${classId}/members`)
  }
}

