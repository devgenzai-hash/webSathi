import axios from 'axios';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Attach token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 - redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  register: (data: { email: string; password: string; full_name?: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
};

// Sites
export const sitesAPI = {
  list: () => api.get('/sites/'),
  create: (data: { site_name: string; domain: string }) =>
    api.post('/sites/', data),
  get: (id: string) => api.get(`/sites/${id}`),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/sites/${id}`, data),
  delete: (id: string) => api.delete(`/sites/${id}`),
  verify: (id: string) => api.post(`/sites/${id}/verify`),
};

// Documents
export const documentsAPI = {
  list: (siteId: string) => api.get(`/sites/${siteId}/documents/`),
  upload: (siteId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/sites/${siteId}/documents/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  delete: (siteId: string, docId: string) =>
    api.delete(`/sites/${siteId}/documents/${docId}`),
};

// Conversations & analytics
export const conversationsAPI = {
  list: (siteId: string, skip = 0, limit = 50) =>
    api.get(`/sites/${siteId}/conversations?skip=${skip}&limit=${limit}`),
  get: (siteId: string, sessionId: string) =>
    api.get(`/sites/${siteId}/conversations/${sessionId}`),
  unanswered: (siteId: string) =>
    api.get(`/sites/${siteId}/unanswered`),
  usage: (siteId: string) =>
    api.get(`/sites/${siteId}/usage`),
};

// Leads
export const leadsAPI = {
  list: (siteId: string) => api.get(`/sites/${siteId}/leads`),
};

// Crawler
export const crawlerAPI = {
  start: (siteId: string, url: string) =>
    api.post(`/sites/${siteId}/crawl`, { url }),
  list: (siteId: string) => api.get(`/sites/${siteId}/crawl`),
  getJob: (siteId: string, jobId: string) =>
    api.get(`/sites/${siteId}/crawl/${jobId}`),
};

// A/B Variants
export const variantsAPI = {
  list: (siteId: string) => api.get(`/sites/${siteId}/variants`),
  create: (siteId: string, data: { name: string; system_prompt: string; is_control?: boolean }) =>
    api.post(`/sites/${siteId}/variants`, data),
  update: (siteId: string, variantId: string, data: Record<string, unknown>) =>
    api.patch(`/sites/${siteId}/variants/${variantId}`, data),
  delete: (siteId: string, variantId: string) =>
    api.delete(`/sites/${siteId}/variants/${variantId}`),
};

// Audit
export const auditAPI = {
  forSite: (siteId: string) => api.get(`/sites/${siteId}/audit`),
  forUser: () => api.get('/audit'),
};

// Models
export const modelsAPI = {
  list: () => api.get('/models/'),
  providers: () => api.get('/models/providers'),
};

export default api;
