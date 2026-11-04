import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { predictionService } from '../../services/predictionService'

export const fetchPrediction = createAsyncThunk(
  'predictions/fetch',
  async (transactionId, { rejectWithValue }) => {
    try {
      return await predictionService.getByTransactionId(transactionId)
    } catch (err) {
      return rejectWithValue(err.response?.data?.message || 'Not found')
    }
  }
)

export const fetchStats = createAsyncThunk(
  'predictions/stats',
  async (_, { rejectWithValue }) => {
    try {
      return await predictionService.getStats()
    } catch (err) {
      return rejectWithValue(err.response?.data?.message || 'Failed')
    }
  }
)

const predictionSlice = createSlice({
  name: 'predictions',
  initialState: {
    byTransactionId: {},
    stats: null,
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchPrediction.fulfilled, (state, action) => {
        const p = action.payload
        state.byTransactionId[p.transaction?.id] = p
      })
      .addCase(fetchStats.pending, (state) => { state.loading = true })
      .addCase(fetchStats.fulfilled, (state, action) => {
        state.loading = false
        state.stats = action.payload
      })
      .addCase(fetchStats.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
  },
})

export default predictionSlice.reducer
