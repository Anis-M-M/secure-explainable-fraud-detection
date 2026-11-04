import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Link } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'
import { fetchStats } from '../store/slices/predictionSlice'
import { fetchTransactions } from '../store/slices/transactionSlice'
import StatCard from '../components/Common/StatCard'
import Spinner from '../components/Common/Spinner'
import { format } from 'date-fns'

// Model comparison data (static until backend metrics endpoint returns live data)
const MODEL_COMPARISON = [
  { name: 'Rule-Based', f1: 0.70, precision: 0.75, recall: 0.65 },
  { name: 'Log. Reg.',  f1: 0.76, precision: 0.82, recall: 0.71 },
  { name: 'XGBoost',   f1: 0.83, precision: 0.89, recall: 0.78 },
  { name: 'Neural Net',f1: 0.84, precision: 0.87, recall: 0.82 },
]

export default function DashboardPage() {
  const dispatch = useDispatch()
  const { stats, loading: statsLoading } = useSelector((s) => s.predictions)
  const { items: transactions, loading: txLoading } = useSelector((s) => s.transactions)
  const [metric, setMetric] = useState('f1')

  useEffect(() => {
    dispatch(fetchStats())
    dispatch(fetchTransactions({ page: 0, size: 5 }))
  }, [dispatch])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-0.5">System overview and model comparison</p>
      </div>

      {/* Stats */}
      {statsLoading ? (
        <div className="flex justify-center py-8"><Spinner size="lg" /></div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Total Predictions"
            value={stats?.total_predictions?.toLocaleString() ?? '—'}
            color="blue"
            icon={DatabaseIcon}
          />
          <StatCard
            label="Fraudulent"
            value={stats?.fraudulent?.toLocaleString() ?? '—'}
            sub={stats ? `${(stats.fraud_rate * 100).toFixed(2)}% fraud rate` : ''}
            color="red"
            icon={AlertIcon}
          />
          <StatCard
            label="Legitimate"
            value={stats?.legitimate?.toLocaleString() ?? '—'}
            color="green"
            icon={CheckIcon}
          />
          <StatCard
            label="Avg Inference"
            value={stats ? `${Math.round(stats.avg_inference_ms)} ms` : '—'}
            sub="per transaction"
            color="amber"
            icon={ClockIcon}
          />
        </div>
      )}

      {/* Model Comparison */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="font-semibold text-gray-900">Model Comparison</h2>
            <p className="text-xs text-gray-400">Rule-Based vs LR vs XGBoost vs Neural Network</p>
          </div>
          <div className="flex gap-1">
            {['f1', 'precision', 'recall'].map((m) => (
              <button
                key={m}
                onClick={() => setMetric(m)}
                className={`px-3 py-1 text-xs rounded-lg font-medium transition-colors ${
                  metric === m
                    ? 'bg-brand-600 text-white'
                    : 'text-gray-500 hover:bg-gray-100'
                }`}
              >
                {m === 'f1' ? 'F1' : m.charAt(0).toUpperCase() + m.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={MODEL_COMPARISON} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis domain={[0, 1]} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v) => (v * 100).toFixed(1) + '%'} />
            <Bar dataKey={metric} radius={[4, 4, 0, 0]}>
              {MODEL_COMPARISON.map((_, i) => (
                <Cell key={i} fill={['#94a3b8','#60a5fa','#3b82f6','#1d4ed8'][i]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Transactions */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-900">Recent Transactions</h2>
          <Link to="/transactions" className="text-xs text-brand-600 hover:underline">View all →</Link>
        </div>

        {txLoading ? (
          <div className="flex justify-center py-6"><Spinner /></div>
        ) : transactions.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-6">No transactions yet</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  {['ID', 'Amount', 'Merchant', 'Date', 'Result'].map((h) => (
                    <th key={h} className="text-left text-xs text-gray-400 font-medium py-2 pr-4">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {transactions.map((tx) => (
                  <tr key={tx.id} className="hover:bg-gray-50 transition-colors">
                    <td className="py-2.5 pr-4 font-mono text-xs text-gray-500">{tx.transactionId}</td>
                    <td className="py-2.5 pr-4 font-medium">${Number(tx.amount).toFixed(2)}</td>
                    <td className="py-2.5 pr-4 text-gray-600">{tx.merchant || '—'}</td>
                    <td className="py-2.5 pr-4 text-gray-400 text-xs">
                      {tx.createdAt ? format(new Date(tx.createdAt), 'MMM d, HH:mm') : '—'}
                    </td>
                    <td className="py-2.5">
                      {tx.prediction ? (
                        tx.prediction.finalPrediction === 1
                          ? <span className="badge-fraud">Fraud</span>
                          : <span className="badge-legit">Legit</span>
                      ) : (
                        <span className="text-xs text-gray-300">Pending</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

// Icons
function DatabaseIcon(p) { return <svg {...p} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" /></svg> }
function AlertIcon(p) { return <svg {...p} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg> }
function CheckIcon(p) { return <svg {...p} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> }
function ClockIcon(p) { return <svg {...p} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> }
