import { useAuth } from '../../hooks/useAuth'

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 shrink-0">
      <h2 className="text-sm font-semibold text-gray-500 tracking-wide uppercase">
        Fraud Detection System
      </h2>

      {user && (
        <div className="flex items-center gap-4">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium text-gray-900">{user.firstName || user.username}</p>
            <p className="text-xs text-gray-400">{user.role}</p>
          </div>
          <div className="w-8 h-8 rounded-full bg-brand-600 text-white flex items-center justify-center text-sm font-semibold">
            {(user.firstName?.[0] || user.username?.[0] || '?').toUpperCase()}
          </div>
          <button
            onClick={logout}
            className="text-xs text-gray-500 hover:text-danger-600 transition-colors"
            title="Sign out"
          >
            Sign out
          </button>
        </div>
      )}
    </header>
  )
}
