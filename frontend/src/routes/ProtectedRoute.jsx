import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
export function ProtectedRoute(){const {isOwner,loading}=useAuth();const location=useLocation();if(loading)return <main className="login-page"><div className="skeleton" style={{width:280}}/></main>;return isOwner?<Outlet/>:<Navigate to="/login" state={{from:location}} replace/>}
