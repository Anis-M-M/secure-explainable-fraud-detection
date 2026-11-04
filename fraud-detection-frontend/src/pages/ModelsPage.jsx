import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer,
} from 'recharts'

const MODELS = [
  { name: 'Rule-Based',          accuracy: 0.75, precision: 0.75, recall: 0.65, f1: 0.70, auc: 0.72 },
  { name: 'Logistic Regression', accuracy: 0.82, precision: 0.82, recall: 0.71, f1: 0.76, auc: 0.85 },
  { name: 'XGBoost',             accuracy: 0.89, precision: 0.89, recall: 0.78, f1: 0.83, auc: 0.95 },
  { name: 'Neural Network',      accuracy: 0.87, precision: 0.87, recall: 0.82, f1: 0.84, auc: 0.93 },
]

const COLORS = ['#94a3b8', '#60a5fa', '#3b82f6', '#1d4ed8']

const RADAR_DATA = ['Accuracy','Precision','Recall','F1','AUC'].map((metric) => {
  const row = { metric }
  MODELS.forEach((m) => { row[m.name] = m[metric.toLowerCase()] ?? m['f1'] })
  return row
})

export default function ModelsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900">Model Comparison</h1>
        <p className="text-sm text-gray-500 mt-0.5">RQ1: Performance comparison across four detection paradigms</p>
      </div>

      {/* Metrics table */}
      <div className="card p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              {['Model','Accuracy','Precision','Recall','F1-Score','ROC-AUC'].map((h) => (
                <th key={h} className="text-left text-xs font-semibold text-gray-500 px-5 py-3">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {MODELS.map((m, i) => (
              <tr key={m.name} className="hover:bg-gray-50">
                <td className="px-5 py-3 font-medium text-gray-900 flex items-center gap-2">
                  <span className="w-3 h-3 rounded-sm" style={{ background: COLORS[i] }} />
                  {m.name}
                  {m.f1 === Math.max(...MODELS.map((x) => x.f1)) && (
                    <span className="text-xs bg-success-50 text-success-600 px-2 py-0.5 rounded-full font-semibold">Best</span>
                  )}
                </td>
                {['accuracy','precision','recall','f1','auc'].map((k) => (
                  <td key={k} className="px-5 py-3">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{(m[k] * 100).toFixed(1)}%</span>
                      <div className="flex-1 h-1.5 bg-gray-100 rounded-full max-w-[60px]">
                        <div className="h-1.5 rounded-full" style={{ width: `${m[k] * 100}%`, background: COLORS[i] }} />
                      </div>
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Bar + Radar side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className="card">
          <h2 className="font-semibold mb-4 text-gray-900">F1-Score Comparison</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={MODELS} margin={{ left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis domain={[0.5, 1]} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v) => `${(v * 100).toFixed(1)}%`} />
              <Bar dataKey="f1" name="F1-Score" radius={[4,4,0,0]}>
                {MODELS.map((_, i) => (
                  <rect key={i} fill={COLORS[i]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2 className="font-semibold mb-4 text-gray-900">Radar Comparison</h2>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={RADAR_DATA}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11 }} />
              <PolarRadiusAxis domain={[0.5, 1]} tick={{ fontSize: 9 }} />
              {MODELS.map((m, i) => (
                <Radar key={m.name} name={m.name} dataKey={m.name}
                  stroke={COLORS[i]} fill={COLORS[i]} fillOpacity={0.1} />
              ))}
              <Legend iconSize={10} wrapperStyle={{ fontSize: 11 }} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Grouped bar */}
      <div className="card">
        <h2 className="font-semibold mb-4 text-gray-900">All Metrics Side-by-Side</h2>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart
            data={['Accuracy','Precision','Recall','F1-Score','ROC-AUC'].map((metric, mi) => {
              const row = { metric }
              MODELS.forEach((m) => {
                row[m.name] = [m.accuracy, m.precision, m.recall, m.f1, m.auc][mi]
              })
              return row
            })}
            margin={{ left: -15 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="metric" tick={{ fontSize: 11 }} />
            <YAxis domain={[0.5, 1]} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v) => `${(v * 100).toFixed(1)}%`} />
            <Legend iconSize={10} wrapperStyle={{ fontSize: 11 }} />
            {MODELS.map((m, i) => (
              <Bar key={m.name} dataKey={m.name} fill={COLORS[i]} radius={[3,3,0,0]} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Research notes */}
      <div className="card bg-brand-50 border-brand-200">
        <h3 className="font-semibold text-brand-900 mb-2">Research Notes (RQ1)</h3>
        <ul className="text-sm text-brand-800 space-y-1 list-disc list-inside">
          <li>XGBoost achieves highest precision (89%) — lowest false-positive rate</li>
          <li>Neural Network achieves highest recall (82%) — fewest missed frauds</li>
          <li>Neural Network achieves best F1 (84%) overall</li>
          <li>Rule-Based provides interpretable baseline but lower performance</li>
          <li>Ensemble combines strengths: Rule 15% · LR 20% · XGB 35% · NN 30%</li>
        </ul>
      </div>
    </div>
  )
}
