import { createContext, useContext } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { loginRequest, logoutRequest, meRequest } from '../api/endpoints/auth'
const AuthContext = createContext()
export function AuthProvider({ children }) {
  const client = useQueryClient(); const hasToken = Boolean(localStorage.getItem('accessToken'))
  const session = useQuery({ queryKey:['session'], queryFn:meRequest, enabled:hasToken, retry:false, staleTime:Infinity })
  const loginMutation = useMutation({ mutationFn: loginRequest, onSuccess: (data) => { localStorage.setItem('accessToken',data.access); localStorage.setItem('refreshToken',data.refresh); client.setQueryData(['session'],data.user) } })
  const logout = async () => { const refresh=localStorage.getItem('refreshToken'); try { if(refresh) await logoutRequest(refresh) } finally { localStorage.removeItem('accessToken'); localStorage.removeItem('refreshToken'); client.removeQueries({queryKey:['session']}) } }
  return <AuthContext.Provider value={{ user:session.data ?? null, isOwner:Boolean(session.data), login:loginMutation.mutateAsync, logout, loading:hasToken && session.isLoading, loginError:loginMutation.error }}>{children}</AuthContext.Provider>
}
export const useAuth = () => useContext(AuthContext)
