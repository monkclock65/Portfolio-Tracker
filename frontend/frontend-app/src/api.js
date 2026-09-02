
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
export default api;

export default api;


