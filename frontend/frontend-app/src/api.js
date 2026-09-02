
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://portfolio-tracker-actk.onrender.com',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token && token !== 'null' && token !== 'undefined') {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: attempt refresh once on 401; if refresh missing/failed, clear auth and redirect
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (!originalRequest) return Promise.reject(error);

    const status = error.response?.status;
    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken || refreshToken === 'null' || refreshToken === 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.dispatchEvent(new Event('auth-change'));
        try { window.location.replace('/welcome'); } catch (e) {}
        return Promise.reject(error);
      }

      try {
        // Use raw axios to avoid interceptor recursion
        const resp = await axios.post(`${api.defaults.baseURL}/auth/refresh`, {}, {
          headers: { Authorization: `Bearer ${refreshToken}` },
        });

        const newAccess = resp.data?.access_token;
        if (newAccess) {
          localStorage.setItem('access_token', newAccess);
          window.dispatchEvent(new Event('auth-change'));
          originalRequest.headers = originalRequest.headers || {};
          originalRequest.headers.Authorization = `Bearer ${newAccess}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.dispatchEvent(new Event('auth-change'));
        try { window.location.replace('/welcome'); } catch (e) {}
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;


