import axios from 'axios';

const DEFAULT_API_PORT = '5001';
const DEFAULT_API_PATH = '/api/v1';
const DEFAULT_QA_API_URL = 'https://ineo-pbl-entrega.onrender.com/api/v1';
const LOCAL_HOSTNAMES = new Set(['localhost', '127.0.0.1', '::1']);

const resolveApiUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL?.trim();

  if (envUrl) {
    return envUrl.replace(/\/+$/, '');
  }

  if (typeof window !== 'undefined' && LOCAL_HOSTNAMES.has(window.location.hostname)) {
    const { protocol, hostname } = window.location;
    return `${protocol}//${hostname}:${DEFAULT_API_PORT}${DEFAULT_API_PATH}`;
  }

  // En despliegues de QA nunca se debe reutilizar el dominio de Vercel con
  // el puerto local 5001. Render expone el servicio mediante HTTPS (443) y
  // administra internamente el puerto PORT=10000.
  return DEFAULT_QA_API_URL;
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
      delete api.defaults.headers.Authorization;
      if (api.defaults.headers.common) delete api.defaults.headers.common.Authorization;
    }
    return Promise.reject(error);
  }
);

export default api;
