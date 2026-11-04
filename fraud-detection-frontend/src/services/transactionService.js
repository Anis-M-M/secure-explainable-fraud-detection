import api from './api'

export const transactionService = {
  getAll: async (page = 0, size = 20) => {
    const { data } = await api.get('/transactions', { params: { page, size, sort: 'createdAt,desc' } })
    return data
  },
  getById: async (id) => {
    const { data } = await api.get(`/transactions/${id}`)
    return data
  },
  create: async (payload) => {
    const { data } = await api.post('/transactions', payload)
    return data
  },
  getByDateRange: async (startDate, endDate, page = 0, size = 20) => {
    const { data } = await api.get('/transactions/date-range', {
      params: { startDate, endDate, page, size },
    })
    return data
  },
}
