import api from './client'

// Thin wrappers around the dahej_insp endpoints. Components stay declarative;
// any API-shape changes happen here in one place.

export const plantsApi = {
  list:   () => api.get('/dahej/plants/').then(r => r.data),
  create: (payload) => api.post('/dahej/plants/', payload).then(r => r.data),
  update: (id, payload) => api.put(`/dahej/plants/${id}/`, payload).then(r => r.data),
  remove: (id) => api.delete(`/dahej/plants/${id}/`),
}

export const jobTypesApi = {
  list:   () => api.get('/dahej/job-types/').then(r => r.data),
  create: (payload) => api.post('/dahej/job-types/', payload).then(r => r.data),
  update: (id, payload) => api.put(`/dahej/job-types/${id}/`, payload).then(r => r.data),
  remove: (id) => api.delete(`/dahej/job-types/${id}/`),
}

export const jobsApi = {
  list:   (params) => api.get('/dahej/jobs/', { params }).then(r => r.data),
  create: (payload) => api.post('/dahej/jobs/', payload).then(r => r.data),
  update: (id, payload) => api.put(`/dahej/jobs/${id}/`, payload).then(r => r.data),
  remove: (id) => api.delete(`/dahej/jobs/${id}/`),
  ranking: (params) => api.get('/dahej/jobs/ranking/', { params }).then(r => r.data),
}

export const jobFilesApi = {
  list: (jobId) => api.get('/dahej/job-files/', { params: { job: jobId } }).then(r => r.data),
  upload: (jobId, file) => {
    const fd = new FormData()
    fd.append('job', jobId)
    fd.append('file', file)
    return api.post('/dahej/job-files/', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data)
  },
  remove: (id) => api.delete(`/dahej/job-files/${id}/`),
}

export const usersApi = {
  list: () => api.get('/auth/users/').then(r => r.data),
}

export const overtimesApi = {
  list:   (params) => api.get('/dahej/overtimes/', { params }).then(r => r.data),
  create: (payload) => api.post('/dahej/overtimes/', payload).then(r => r.data),
  update: (id, payload) => api.put(`/dahej/overtimes/${id}/`, payload).then(r => r.data),
  remove: (id) => api.delete(`/dahej/overtimes/${id}/`),
  ranking: (params) => api.get('/dahej/overtimes/ranking/', { params }).then(r => r.data),
}
