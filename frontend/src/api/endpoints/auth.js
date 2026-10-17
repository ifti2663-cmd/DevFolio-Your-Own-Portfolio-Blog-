import api from '../axios'
export const loginRequest = (credentials) => api.post('/auth/login/', credentials).then(r => r.data)
export const meRequest = () => api.get('/auth/me/').then(r => r.data)
export const logoutRequest = (refresh) => api.post('/auth/logout/', { refresh })
export const changePassword = (data) => api.post('/auth/change-password/', data).then(r => r.data)
