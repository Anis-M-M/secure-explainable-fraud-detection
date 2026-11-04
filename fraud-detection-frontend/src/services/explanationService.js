import api from './api'

export const explanationService = {
  getShap: async (transactionId) => {
    const { data } = await api.get(`/explanations/transaction/${transactionId}/shap`)
    return data
  },
  getLime: async (transactionId) => {
    const { data } = await api.get(`/explanations/transaction/${transactionId}/lime`)
    return data
  },
  getStability: async (transactionId) => {
    const { data } = await api.get(`/explanations/transaction/${transactionId}/stability`)
    return data
  },
  getAll: async (transactionId) => {
    const { data } = await api.get(`/explanations/transaction/${transactionId}`)
    return data
  },
}
