import api from './api'

export const predictionService = {
  getByTransactionId: async (transactionId) => {
    const { data } = await api.get(`/predictions/transaction/${transactionId}`)
    return data
  },
  getStats: async () => {
    const { data } = await api.get('/predictions/stats')
    return data
  },
}
