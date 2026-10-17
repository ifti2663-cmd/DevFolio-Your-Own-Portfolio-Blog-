import api from '../axios'
const query = (params = {}) => ({ params })
export const postsApi = {
  list: params => api.get('/posts/', query(params)).then(r => r.data), get: slug => api.get(`/posts/${slug}/`).then(r => r.data),
  create: d => api.post('/posts/', d, { headers:{'Content-Type':'multipart/form-data'} }).then(r=>r.data), update:(slug,d)=>api.patch(`/posts/${slug}/`,d,{headers:{'Content-Type':'multipart/form-data'}}).then(r=>r.data), remove:slug=>api.delete(`/posts/${slug}/`),
  like: slug => api.post(`/posts/${slug}/like/`).then(r=>r.data), comments: slug=>api.get(`/posts/${slug}/comments/`).then(r=>r.data), comment:(slug,d)=>api.post(`/posts/${slug}/comments/`,d).then(r=>r.data)
}
export const commentsApi = { list: params => api.get('/comments/',query(params)).then(r=>r.data), update:(id,d)=>api.patch(`/comments/${id}/`,d).then(r=>r.data), remove:id=>api.delete(`/comments/${id}/`) }
export const dashboardApi = { stats: () => api.get('/dashboard/stats/').then(r=>r.data) }
