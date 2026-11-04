import { useSelector, useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { login, logout, loadCurrentUser } from '../store/slices/authSlice'

export function useAuth() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { user, token, loading, error } = useSelector((s) => s.auth)

  const handleLogin = async (credentials) => {
    const result = await dispatch(login(credentials))
    if (login.fulfilled.match(result)) navigate('/dashboard')
  }

  const handleLogout = () => {
    dispatch(logout())
    navigate('/login')
  }

  const refreshUser = () => dispatch(loadCurrentUser())

  return { user, token, loading, error, login: handleLogin, logout: handleLogout, refreshUser }
}
