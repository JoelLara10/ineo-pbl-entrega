import { clearClinicalCache, purgeLegacyClinicalStorage } from '../services/clinicalCache';
import { clearOfflineQueue } from '../services/offlineQueue';
import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext({});
export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStoredData();
  }, []);

  useEffect(() => {
    const expire = () => { setUser(null); };
    const storageChanged = (event) => {
      if (event.key === '@ineo_token' || event.key === '@ineo_user' || event.key === null) {
        clearClinicalCache(); clearOfflineQueue();
        clearAuthorization(); setUser(null);
      }
    };
    window.addEventListener('ineo-session-expired', expire);
    window.addEventListener('storage', storageChanged);
    return () => {
      window.removeEventListener('ineo-session-expired', expire);
      window.removeEventListener('storage', storageChanged);
    };
  }, []);

  const clearAuthorization = () => {
    delete api.defaults.headers.Authorization;
    if (api.defaults.headers.common) delete api.defaults.headers.common.Authorization;
  };

  const loadStoredData = () => {
    try {
      const storedUser = localStorage.getItem('@ineo_user');
      const storedToken = localStorage.getItem('@ineo_token');

      if (storedUser && storedToken) {
        setUser(JSON.parse(storedUser));
        api.defaults.headers.Authorization = `Bearer ${storedToken}`;
      }
    } catch (err) {
      localStorage.removeItem('@ineo_token');
      localStorage.removeItem('@ineo_user');
      clearAuthorization();
      console.error('Error cargando sesión:', err);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    clearClinicalCache(); purgeLegacyClinicalStorage(); clearOfflineQueue();
    setError(null);
    localStorage.removeItem('@ineo_token');
    localStorage.removeItem('@ineo_user');
    clearAuthorization();
    try {
      const response = await api.post('/auth/login', { username: username.trim(), password });
      const { token, user: userData } = response.data;

      localStorage.setItem('@ineo_token', token);
      localStorage.setItem('@ineo_user', JSON.stringify(userData));
      api.defaults.headers.Authorization = `Bearer ${token}`;
      setUser(userData);

      return { success: true };
    } catch (err) {
      const message = err.response?.data?.error || 'Error de conexión';
      setError(message);
      return { success: false, error: message };
    }
  };

  const logout = () => {
    clearClinicalCache(); purgeLegacyClinicalStorage(); clearOfflineQueue();
    const token = localStorage.getItem('@ineo_token');
    if (token) {
      try {
        const logoutRequest = api.post('/auth/logout', {}, {
          headers: { Authorization: `Bearer ${token}` },
        });
        logoutRequest?.catch?.(() => {});
      } catch {
        // La sesión local debe cerrarse aunque el servidor no esté disponible.
      }
    }
    localStorage.removeItem('@ineo_token');
    localStorage.removeItem('@ineo_user');
    clearAuthorization();
    setError(null);
    setUser(null);
  };

  const updateUser = (userData) => {
    setUser(userData);
    localStorage.setItem('@ineo_user', JSON.stringify(userData));
  };

  return (
    <AuthContext.Provider value={{ user, loading, error, login, logout, updateUser, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};
