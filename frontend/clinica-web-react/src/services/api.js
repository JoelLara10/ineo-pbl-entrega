import axios from 'axios';

const DEFAULT_API_PORT = '5001';
const DEFAULT_API_PATH = '/api/v1';

const resolveApiUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL?.trim();

  if (envUrl) {
    return envUrl.replace(/\/+$/, '');
  }

  if (typeof window !== 'undefined') {
    const { protocol, hostname } = window.location;
    const resolvedHost = hostname || 'localhost';
    return `${protocol}//${resolvedHost}:${DEFAULT_API_PORT}${DEFAULT_API_PATH}`;
  }

  return `http://localhost:${DEFAULT_API_PORT}${DEFAULT_API_PATH}`;
};

const API_URL = resolveApiUrl();

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// 🔐 Interceptor: agregar token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('@ineo_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// 🚨 Interceptor: token inválido
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('@ineo_token');
      localStorage.removeItem('@ineo_user');
    }
    return Promise.reject(error);
  }
);

export default api;