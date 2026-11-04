import api from './api'

export const authService = {
  login: async (credentials) => {
    const { data } = await api.post('/auth/login', credentials)
    return data
  },
  register: async (payload) => {
    const { data } = await api.post('/auth/register', payload)
    return data
  },
  getCurrentUser: async () => {
    const token = localStorage.getItem('token')
    const { data } = await api.get('/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
    return data
  },
  refresh: async () => {
    const { data } = await api.post('/auth/refresh')
    return data
  },
}
