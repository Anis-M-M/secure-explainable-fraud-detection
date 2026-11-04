import { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, ReferenceLine,
} from 'recharts'
import toast from 'react-hot-toast'
import { explanationService } from '../services/explanationService'
import Spinner from '../components/Common/Spinner'

const FEATURE_COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#f59e0b', '#10b981']

export default function ExplanationsPage() {
  const [searchParams] = useSearchParams()
  const transactionId = searchParams.get('txId')

  const [shap, setShap] = useState(null)
  const [lime, setLime] = useState(null)
  const [stability, setStability] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('shap')

  useEffect(() => {
    if (!transactionId) return
    setLoading(true)
    setError('')

    Promise.all([
      explanationService.getShap(transactionId),
      explanationService.getLime(transactionId),
      explanationService.getStability(transactionId),
    ])
      .then(([shapData, limeData, stabilityData]) => {
        setShap(shapData)
        setLime(limeData)
        setStability(stabilityData)
      })
      .catch((err) => {
        const msg = err.response?.data?.message || 'Failed to load explanations'
        setError(msg)
        toast.error(msg)
      })
      .finally(() => setLoading(false))
  }, [transactionId])

  if (!transactionId) {
    return (
      <div className="card space-y-3">
        <h1 className="text-xl font-bold text-gray-900">Explanations</h1>
        <p className="text-sm text-gray-500">
          Open this page from a transaction detail screen to view SHAP, LIME, and stability results.
        </p>
      </div>
    )
  }

  if (loading) {
    return <div className="flex justify-center py-20"><Spinner size="lg" /></div>
  }

  if (error) {
    return (
      <div className="card space-y-3">
        <h1 className="text-xl font-bold text-gray-900">Explanations</h1>
        <p className="text-sm text-danger-600">{error}</p>
        <Link to={`/transactions/${transactionId}`} className="btn-secondary w-fit">
          Back to transaction
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Explanations</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Transaction #{transactionId} — RQ2: SHAP vs LIME stability & attribution comparison
          </p>
        </div>
        <Link to={`/transactions/${transactionId}`} className="btn-secondary">
          Back to transaction
        </Link>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-gray-200">
        {[
          { id: 'shap',      label: 'SHAP',         avail: !!shap },
          { id: 'lime',      label: 'LIME',         avail: !!lime },
          { id: 'stability', label: 'Stability',    avail: !!stability },
          { id: 'compare',   label: 'SHAP vs LIME', avail: !!(shap && lime) },
        ].map(({ id, label, avail }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors -mb-px ${
              activeTab === id
                ? 'border-brand-600 text-brand-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {label}
            {avail && <span className="ml-1.5 text-success-500 text-xs">✓</span>}
          </button>
        ))}
      </div>

      {activeTab === 'shap'      && <SHAPPanel data={shap} />}
      {activeTab === 'lime'      && <LIMEPanel data={lime} />}
      {activeTab === 'stability' && <StabilityPanel data={stability} />}
      {activeTab === 'compare'   && <ComparePanel shap={shap} lime={lime} />}
    </div>
  )
}

// ── SHAP Panel ────────────────────────────────────────────────────────────────

function SHAPPanel({ data }) {
  if (!data) return <EmptyCard msg="SHAP explanation not available" />

  const parsed = parseJson(data.featureImportanceJson)
  const shapValues = parsed?.shap_values || {}
  const topFeatures = parsed?.top_features || []
  const baseValue = parsed?.base_value ?? 0

  const chartData = Object.entries(shapValues)
    .map(([feature, value]) => ({ feature, value: +Number(value).toFixed(4) }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))

  return (
    <div className="space-y-4">
      <div className="card">
        <div className="flex items-center justify-between mb-1">
          <h2 className="font-semibold text-gray-900">SHAP Feature Attributions</h2>
          <span className="text-xs text-gray-400">Base value: {Number(baseValue).toFixed(4)}</span>
        </div>
        <p className="text-xs text-gray-500 mb-4">
          Positive values push toward{' '}
          <span className="text-danger-600 font-medium">fraud</span>; negative toward{' '}
          <span className="text-success-600 font-medium">legitimate</span>
        </p>

        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData} layout="vertical" margin={{ left: 30, right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="feature" tick={{ fontSize: 11 }} width={120} />
              <Tooltip formatter={(v) => Number(v).toFixed(4)} />
              <ReferenceLine x={0} stroke="#9ca3af" strokeWidth={1.5} />
              <Bar dataKey="value" radius={[0, 3, 3, 0]}>
                {chartData.map((d, i) => (
                  <Cell key={i} fill={d.value >= 0 ? '#ef4444' : '#22c55e'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm text-gray-400 text-center py-8">No SHAP values available</p>
        )}
      </div>

      {topFeatures.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-3">Top Contributing Features</h3>
          <div className="space-y-2.5">
            {topFeatures.map((f, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <span
                    className="w-2.5 h-2.5 rounded-full shrink-0"
                    style={{ background: FEATURE_COLORS[i % FEATURE_COLORS.length] }}
                  />
                  <span className="font-medium text-gray-800">{f.feature}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                    f.impact === 'HIGH'
                      ? 'bg-danger-50 text-danger-600'
                      : 'bg-warn-50 text-warn-600'
                  }`}>
                    {f.impact}
                  </span>
                </div>
                <span className={`font-mono text-xs ${
                  f.shap_value >= 0 ? 'text-danger-600' : 'text-success-600'
                }`}>
                  {Number(f.shap_value).toFixed(4)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ── LIME Panel ────────────────────────────────────────────────────────────────

function LIMEPanel({ data }) {
  if (!data) return <EmptyCard msg="LIME explanation not available" />

  const parsed = parseJson(data.featureImportanceJson)
  const weights = parsed?.local_weights || {}
  const topFeatures = parsed?.top_features || []
  const intercept = parsed?.intercept ?? 0

  const chartData = Object.entries(weights)
    .map(([feature, weight]) => ({
      feature: feature.split(' ')[0],
      weight: +Number(weight).toFixed(4),
    }))
    .sort((a, b) => Math.abs(b.weight) - Math.abs(a.weight))

  return (
    <div className="space-y-4">
      <div className="card">
        <div className="flex items-center justify-between mb-1">
          <h2 className="font-semibold text-gray-900">LIME Local Feature Weights</h2>
          <span className="text-xs text-gray-400">
            Intercept: {Number(intercept).toFixed(4)}
          </span>
        </div>
        <p className="text-xs text-gray-500 mb-4">
          Local linear approximation around this specific transaction
        </p>

        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData} layout="vertical" margin={{ left: 30, right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="feature" tick={{ fontSize: 11 }} width={120} />
              <Tooltip formatter={(v) => Number(v).toFixed(4)} />
              <ReferenceLine x={0} stroke="#9ca3af" strokeWidth={1.5} />
              <Bar dataKey="weight" radius={[0, 3, 3, 0]}>
                {chartData.map((d, i) => (
                  <Cell key={i} fill={d.weight >= 0 ? '#8b5cf6' : '#06b6d4'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm text-gray-400 text-center py-8">No LIME weights available</p>
        )}
      </div>

      {topFeatures.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-3">Feature Contributions</h3>
          <div className="space-y-2.5">
            {topFeatures.map((f, i) => (
              <div key={i} className="flex items-center justify-between gap-4 text-sm">
                <div className="flex items-center gap-2 shrink-0">
                  <span
                    className="w-2.5 h-2.5 rounded-full shrink-0"
                    style={{ background: FEATURE_COLORS[i % FEATURE_COLORS.length] }}
                  />
                  <span className="font-medium text-gray-800">{f.feature}</span>
                </div>
                <span className="text-xs text-gray-500 text-right truncate">
                  {f.contribution}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ── Stability Panel ───────────────────────────────────────────────────────────

function StabilityPanel({ data }) {
  if (!data) return <EmptyCard msg="Stability analysis not available" />

  // Support both snake_case (from ML service direct) and camelCase (via Java)
  const analysis = data.stabilityAnalysis || data
  const score        = analysis.stability_score        ?? analysis.stabilityScore        ?? 0
  const agreement    = analysis.shap_lime_agreement    ?? analysis.shapLimeAgreement      ?? 0
  const perturbations = analysis.perturbation_count    ?? analysis.perturbationCount      ?? 100
  const recs         = analysis.recommendations        || []

  const scoreColor = (v) =>
    v >= 0.85 ? 'text-success-600' : v >= 0.70 ? 'text-warn-600' : 'text-danger-600'

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { label: 'Stability Score',      value: score,        pct: true,  desc: 'Feature ranking consistency' },
          { label: 'SHAP–LIME Agreement',  value: agreement,    pct: true,  desc: 'Spearman correlation' },
          { label: 'Perturbations',        value: perturbations, pct: false, desc: 'Noise trials run' },
        ].map(({ label, value, pct, desc }) => (
          <div key={label} className="card text-center">
            <p className="text-xs text-gray-400 uppercase tracking-wide font-medium mb-1">{label}</p>
            <p className={`text-3xl font-bold ${pct ? scoreColor(value) : 'text-gray-900'}`}>
              {pct ? `${(Number(value) * 100).toFixed(1)}%` : value}
            </p>
            <p className="text-xs text-gray-400 mt-1">{desc}</p>
          </div>
        ))}
      </div>

      {recs.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-3">Analysis Recommendations</h3>
          <ul className="space-y-2">
            {recs.map((r, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="mt-0.5 text-brand-500 shrink-0">•</span>
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="card bg-brand-50 border-brand-200">
        <h3 className="font-semibold text-brand-900 mb-2">Research Context (RQ2)</h3>
        <p className="text-sm text-brand-800">
          Stability Score measures how consistently SHAP and LIME rank features
          across {perturbations} small input perturbations. Higher SHAP–LIME agreement
          (Spearman r closer to 1) indicates that both XAI methods reach the same
          conclusions about feature importance, strengthening explanation trustworthiness.
        </p>
      </div>
    </div>
  )
}

// ── Compare Panel ─────────────────────────────────────────────────────────────

function ComparePanel({ shap, lime }) {
  if (!shap || !lime) {
    return <EmptyCard msg="Both SHAP and LIME results are needed for comparison" />
  }

  const shapParsed = parseJson(shap.featureImportanceJson)
  const limeParsed  = parseJson(lime.featureImportanceJson)
  const shapVals    = shapParsed?.shap_values   || {}
  const limeVals    = limeParsed?.local_weights || {}

  const features = [...new Set([...Object.keys(shapVals), ...Object.keys(limeVals)])]
  const chartData = features
    .map((f) => ({
      feature: f,
      shap: Math.abs(+(Number(shapVals[f] || 0).toFixed(4))),
      lime: Math.abs(+(Number(limeVals[f] || 0).toFixed(4))),
    }))
    .sort((a, b) => (b.shap + b.lime) - (a.shap + a.lime))

  return (
    <div className="space-y-4">
      <div className="card">
        <h2 className="font-semibold text-gray-900 mb-1">SHAP vs LIME — Absolute Importance</h2>
        <p className="text-xs text-gray-500 mb-4">
          Higher bars indicate stronger influence on the fraud prediction
        </p>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={chartData} margin={{ left: -10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="feature" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v) => Number(v).toFixed(4)} />
            <Bar dataKey="shap" name="SHAP" fill="#3b82f6" radius={[3, 3, 0, 0]} />
            <Bar dataKey="lime" name="LIME" fill="#8b5cf6" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>

        {/* Legend */}
        <div className="flex gap-4 mt-2 justify-center">
          {[['#3b82f6', 'SHAP'], ['#8b5cf6', 'LIME']].map(([color, label]) => (
            <div key={label} className="flex items-center gap-1.5 text-xs text-gray-600">
              <span className="w-3 h-3 rounded-sm" style={{ background: color }} />
              {label}
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-3">Feature Agreement Table</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 text-xs text-gray-400 font-medium">
              <th className="text-left py-2 pr-4">Feature</th>
              <th className="text-right py-2 pr-4 text-brand-600">|SHAP|</th>
              <th className="text-right py-2 pr-4 text-purple-600">|LIME|</th>
              <th className="text-right py-2">Agreement</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {chartData.map((row) => {
              const diff  = Math.abs(row.shap - row.lime)
              const agree = diff < 0.05 ? 'Strong' : diff < 0.15 ? 'Moderate' : 'Weak'
              const agreeColor = {
                Strong:   'bg-success-50 text-success-600',
                Moderate: 'bg-warn-50 text-warn-600',
                Weak:     'bg-danger-50 text-danger-600',
              }[agree]
              return (
                <tr key={row.feature} className="hover:bg-gray-50">
                  <td className="py-2.5 pr-4 font-medium text-gray-800">{row.feature}</td>
                  <td className="py-2.5 pr-4 text-right font-mono text-xs text-brand-600">
                    {row.shap.toFixed(4)}
                  </td>
                  <td className="py-2.5 pr-4 text-right font-mono text-xs text-purple-600">
                    {row.lime.toFixed(4)}
                  </td>
                  <td className="py-2.5 text-right">
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${agreeColor}`}>
                      {agree}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function parseJson(str) {
  if (!str) return null
  try { return JSON.parse(str) } catch { return null }
}

function EmptyCard({ msg }) {
  return (
    <div className="card text-center text-gray-400 py-12 text-sm">{msg}</div>
  )
}
