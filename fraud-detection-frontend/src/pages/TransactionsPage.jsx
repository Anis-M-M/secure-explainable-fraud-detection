import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Link } from 'react-router-dom'
import { format } from 'date-fns'
import toast from 'react-hot-toast'
import { fetchTransactions, createTransaction } from '../store/slices/transactionSlice'
import Spinner from '../components/Common/Spinner'

export default function TransactionsPage() {
  const dispatch = useDispatch()
  const { items, loading, totalPages, currentPage } = useSelector((s) => s.transactions)
  const [page, setPage] = useState(0)
  const [showForm, setShowForm] = useState(false)

  useEffect(() => {
    dispatch(fetchTransactions({ page, size: 20 }))
  }, [dispatch, page])

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Transactions</h1>
          <p className="text-sm text-gray-500 mt-0.5">All transactions with fraud predictions</p>
        </div>
        <button className="btn-primary" onClick={() => setShowForm((v) => !v)}>
          + New Transaction
        </button>
      </div>

      {showForm && <NewTransactionForm onClose={() => setShowForm(false)} />}

      <div className="card p-0 overflow-hidden">
        {loading ? (
          <div className="flex justify-center py-16"><Spinner size="lg" /></div>
        ) : items.length === 0 ? (
          <p className="text-center text-gray-400 py-16">No transactions found</p>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    {['Transaction ID','Amount','Merchant','Category','Date','Device','Result'].map((h) => (
                      <th key={h} className="text-left text-xs text-gray-500 font-semibold px-4 py-3">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {items.map((tx) => (
                    <tr key={tx.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3 font-mono text-xs text-brand-600">
                        <Link to={`/transactions/${tx.id}`} className="hover:underline">{tx.transactionId}</Link>
                      </td>
                      <td className="px-4 py-3 font-semibold">${Number(tx.amount).toFixed(2)}</td>
                      <td className="px-4 py-3 text-gray-600">{tx.merchant || '—'}</td>
                      <td className="px-4 py-3 text-gray-400 text-xs">{tx.merchantCategory || '—'}</td>
                      <td className="px-4 py-3 text-gray-400 text-xs whitespace-nowrap">
                        {tx.transactionDate ? format(new Date(tx.transactionDate), 'MMM d, yyyy') : '—'}
                      </td>
                      <td className="px-4 py-3 text-gray-400 text-xs">{tx.deviceType || '—'}</td>
                      <td className="px-4 py-3">
                        {tx.prediction ? (
                          <div>
                            {tx.prediction.finalPrediction === 1
                              ? <span className="badge-fraud">Fraud</span>
                              : <span className="badge-legit">Legit</span>}
                            <span className="text-xs text-gray-400 ml-1">
                              {(tx.prediction.finalConfidence * 100).toFixed(0)}%
                            </span>
                          </div>
                        ) : (
                          <span className="text-xs text-gray-300">Pending</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100">
              <span className="text-xs text-gray-400">Page {currentPage + 1} of {totalPages}</span>
              <div className="flex gap-2">
                <button
                  className="btn-secondary py-1 px-3 text-xs"
                  disabled={page === 0}
                  onClick={() => setPage((p) => p - 1)}
                >Prev</button>
                <button
                  className="btn-secondary py-1 px-3 text-xs"
                  disabled={page + 1 >= totalPages}
                  onClick={() => setPage((p) => p + 1)}
                >Next</button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function NewTransactionForm({ onClose }) {
  const dispatch = useDispatch()
  const [form, setForm] = useState({
    transactionId: `TXN-${Date.now()}`,
    amount: '',
    merchant: '',
    merchantCategory: '',
    transactionDate: new Date().toISOString().slice(0, 16),
    userAge: '',
    userLocation: '',
    deviceType: 'Mobile',
  })
  const [submitting, setSubmitting] = useState(false)

  const set = (k) => (e) => setForm((p) => ({ ...p, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await dispatch(createTransaction({
        ...form,
        amount: parseFloat(form.amount),
        userAge: form.userAge ? parseInt(form.userAge) : null,
        transactionDate: new Date(form.transactionDate).toISOString(),
      })).unwrap()
      toast.success('Transaction created — fraud detection running…')
      onClose()
    } catch (err) {
      toast.error(err || 'Failed to create transaction')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="card border border-brand-200 bg-brand-50/30">
      <h3 className="font-semibold text-gray-900 mb-4">New Transaction</h3>
      <form onSubmit={handleSubmit} className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {[
          { k: 'transactionId', label: 'Transaction ID', required: true },
          { k: 'amount',         label: 'Amount (€)',      required: true, type: 'number' },
          { k: 'merchant',       label: 'Merchant' },
          { k: 'merchantCategory', label: 'Category' },
          { k: 'userAge',        label: 'User Age',        type: 'number' },
          { k: 'userLocation',   label: 'Location' },
        ].map(({ k, label, required, type = 'text' }) => (
          <div key={k}>
            <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
            <input className="input" type={type} value={form[k]} onChange={set(k)} required={required} />
          </div>
        ))}

        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Device</label>
          <select className="input" value={form.deviceType} onChange={set('deviceType')}>
            {['Mobile','Desktop','Tablet','Unknown'].map((d) => (
              <option key={d}>{d}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Date & Time</label>
          <input className="input" type="datetime-local" value={form.transactionDate} onChange={set('transactionDate')} required />
        </div>

        <div className="col-span-full flex gap-3 pt-2">
          <button type="submit" className="btn-primary" disabled={submitting}>
            {submitting ? 'Submitting…' : 'Submit & Detect'}
          </button>
          <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
        </div>
      </form>
    </div>
  )
}
