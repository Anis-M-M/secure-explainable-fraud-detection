import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { transactionService } from '../../services/transactionService'

export const fetchTransactions = createAsyncThunk(
  'transactions/fetchAll',
  async ({ page = 0, size = 20 } = {}, { rejectWithValue }) => {
    try {
      return await transactionService.getAll(page, size)
    } catch (err) {
      return rejectWithValue(err.response?.data?.message || 'Failed to load transactions')
    }
  }
)

export const fetchTransaction = createAsyncThunk(
  'transactions/fetchOne',
  async (id, { rejectWithValue }) => {
    try {
      return await transactionService.getById(id)
    } catch (err) {
      return rejectWithValue(err.response?.data?.message || 'Not found')
    }
  }
)

export const createTransaction = createAsyncThunk(
  'transactions/create',
  async (data, { rejectWithValue }) => {
    try {
      return await transactionService.create(data)
    } catch (err) {
      return rejectWithValue(err.response?.data?.message || 'Create failed')
    }
  }
)

const transactionSlice = createSlice({
  name: 'transactions',
  initialState: {
    items: [],
    selected: null,
    totalPages: 0,
    totalElements: 0,
    currentPage: 0,
    loading: false,
    error: null,
  },
  reducers: {
    clearSelected(state) { state.selected = null },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTransactions.pending, (state) => { state.loading = true })
      .addCase(fetchTransactions.fulfilled, (state, action) => {
        state.loading = false
        state.items = action.payload.content
        state.totalPages = action.payload.totalPages ?? 0
        state.totalElements = action.payload.totalElements ?? 0
        state.currentPage = action.payload.number ?? 0
      })
      .addCase(fetchTransactions.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
      .addCase(fetchTransaction.fulfilled, (state, action) => { state.selected = action.payload })
      .addCase(createTransaction.fulfilled, (state, action) => {
        state.items.unshift(action.payload)
      })
  },
})

export const { clearSelected } = transactionSlice.actions
export default transactionSlice.reducer
