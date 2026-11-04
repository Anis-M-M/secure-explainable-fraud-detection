import clsx from 'clsx'

export default function StatCard({ label, value, sub, color = 'blue', icon: Icon }) {
  const colors = {
    blue:  'bg-brand-50  text-brand-600',
    red:   'bg-danger-50  text-danger-600',
    green: 'bg-success-50 text-success-600',
    amber: 'bg-warn-50    text-warn-600',
  }

  return (
    <div className="card flex items-center gap-4">
      {Icon && (
        <div className={clsx('w-11 h-11 rounded-xl flex items-center justify-center shrink-0', colors[color])}>
          <Icon className="w-6 h-6" />
        </div>
      )}
      <div className="min-w-0">
        <p className="text-xs text-gray-500 uppercase tracking-wide font-medium truncate">{label}</p>
        <p className="text-2xl font-bold text-gray-900 leading-tight">{value}</p>
        {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}
