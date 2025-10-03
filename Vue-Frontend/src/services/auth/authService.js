import api from '../api'

export const authService = {
  async login(credentials) {
    return api.post('/auth/login', {
      username: credentials.email,
      password: credentials.password
    })
  },

  async register(userData) {
    return api.post('/auth/register', userData)
  },

  // NEW: Firebase login
  async firebaseLogin(payload) {
    return api.post('/auth/firebase-login', payload)
  },

  async getCurrentUser() {
    return api.get('/auth/me')
  },

  async updateProfile(userData) {
    return api.put('/auth/profile', userData)
  },

  async logout() {
    return api.post('/auth/logout')
  }
}


