import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { format } from 'date-fns'
import { transactionService } from '../services/transactionService'
import { predictionService } from '../services/predictionService'
import Spinner from '../components/Common/Spinner'

export default function TransactionDetailPage() {
  const { id } = useParams()
  const [tx, setTx] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      transactionService.getById(id),
      predictionService.getByTransactionId(id).catch(() => null),
    ]).then(([t, p]) => {
      setTx(t)
      setPrediction(p)
    }).finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>
  if (!tx) return <p className="text-center text-gray-400 py-20">Transaction not found</p>

  const isFraud = prediction?.finalPrediction === 1

  return (
    <div className="max-w-3xl space-y-5">
      <div className="flex items-center gap-3">
        <Link to="/transactions" className="text-sm text-gray-400 hover:text-brand-600">Back to transactions</Link>
        <span className="text-gray-300">/</span>
        <span className="font-mono text-sm text-gray-600">{tx.transactionId}</span>
        {prediction && (
          isFraud
            ? <span className="badge-fraud ml-auto">FRAUD</span>
            : <span className="badge-legit ml-auto">LEGITIMATE</span>
        )}
      </div>

      <div className="card">
        <h2 className="font-semibold mb-4">Transaction Details</h2>
        <dl className="grid grid-cols-2 gap-x-8 gap-y-3 text-sm">
          {[
            ['Transaction ID', tx.transactionId],
            ['Amount', `$${Number(tx.amount).toFixed(2)}`],
            ['Merchant', tx.merchant || '-'],
            ['Category', tx.merchantCategory || '-'],
            ['Date', tx.transactionDate ? format(new Date(tx.transactionDate), 'PPP p') : '-'],
            ['Device', tx.deviceType || '-'],
            ['User Age', tx.userAge ?? '-'],
            ['Location', tx.userLocation || '-'],
          ].map(([k, v]) => (
            <div key={k}>
              <dt className="text-xs text-gray-400 uppercase tracking-wide font-medium">{k}</dt>
              <dd className="font-medium text-gray-900 mt-0.5">{v}</dd>
            </div>
          ))}
        </dl>
      </div>

      {prediction && (
        <div className="card">
          <h2 className="font-semibold mb-4">Model Predictions</h2>
          <div className="space-y-3">
            {[
              { label: 'Rule-Based', prob: prediction.ruleBasedConfidence, pred: prediction.ruleBasedPrediction },
              { label: 'Logistic Regression', prob: prediction.logisticRegressionProbability, pred: prediction.logisticRegressionPrediction },
              { label: 'XGBoost', prob: prediction.xgboostProbability, pred: prediction.xgboostPrediction },
              { label: 'Neural Network', prob: prediction.neuralNetworkProbability, pred: prediction.neuralNetworkPrediction },
            ].map(({ label, prob, pred }) => (
              <div key={label}>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-700 font-medium">{label}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-500 text-xs">{prob != null ? (prob * 100).toFixed(1) + '%' : '-'}</span>
                    {pred === 1
                      ? <span className="badge-fraud">Fraud</span>
                      : <span className="badge-legit">Legit</span>}
                  </div>
                </div>
                {prob != null && (
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-2 rounded-full transition-all ${prob >= 0.5 ? 'bg-danger-500' : 'bg-success-500'}`}
                      style={{ width: `${(prob * 100).toFixed(1)}%` }}
                    />
                  </div>
                )}
              </div>
            ))}

            <div className="pt-3 border-t border-gray-100 flex items-center justify-between">
              <span className="font-semibold text-gray-900">Final (Ensemble)</span>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">{(prediction.finalConfidence * 100).toFixed(1)}%</span>
                {isFraud
                  ? <span className="badge-fraud text-sm px-3 py-1">FRAUD</span>
                  : <span className="badge-legit text-sm px-3 py-1">LEGITIMATE</span>}
              </div>
            </div>
          </div>
        </div>
      )}

      {prediction && (
        <div className="card bg-brand-50 border-brand-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-brand-900">Explanations Available</p>
              <p className="text-xs text-brand-600 mt-0.5">SHAP and LIME explanations with stability analysis</p>
            </div>
            <Link to={`/explanations?txId=${id}`} className="btn-primary text-sm">
              View Explanations
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}
