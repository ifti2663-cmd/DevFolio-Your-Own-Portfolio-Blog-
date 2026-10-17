import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL, headers: { 'Content-Type': 'application/json' } })
api.interceptors.request.use((config) => {
  const access = localStorage.getItem('accessToken'); const visitor = localStorage.getItem('visitorId')
  if (access) config.headers.Authorization = `Bearer ${access}`
  if (visitor) config.headers['X-Visitor-Id'] = visitor
  return config
})
let refreshing = null
api.interceptors.response.use((response) => response, async (error) => {
  const original = error.config
  if (error.response?.status !== 401 || original?._retried || original?.url?.includes('/auth/refresh/')) return Promise.reject(error)
  original._retried = true
  try {
    refreshing ||= axios.post(`${import.meta.env.VITE_API_URL}/auth/refresh/`, { refresh: localStorage.getItem('refreshToken') })
    const { data } = await refreshing; localStorage.setItem('accessToken', data.access); refreshing = null
    original.headers.Authorization = `Bearer ${data.access}`
    return api(original)
  } catch (refreshError) {
    refreshing = null; localStorage.removeItem('accessToken'); localStorage.removeItem('refreshToken')
    if (location.pathname.startsWith('/dashboard')) location.assign('/login')
    return Promise.reject(refreshError)
  }
})
export default api
