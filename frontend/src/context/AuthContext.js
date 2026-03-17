import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import api from '../services/api';
import { getToken, setToken, removeToken, getCurrentUser } from '../services/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setTokenState] = useState(getToken);
  const [loading, setLoading] = useState(true);

  // On mount: validate the stored token by fetching /api/auth/me
  useEffect(() => {
    async function loadUser() {
      const stored = getToken();
      if (!stored) {
        setLoading(false);
        return;
      }
      try {
        const res = await api.get('/api/auth/me');
        setUser(res.data);
      } catch {
        removeToken();
        setUser(null);
        setTokenState(null);
      } finally {
        setLoading(false);
      }
    }
    loadUser();
  }, []);

  const login = useCallback(async (email, password) => {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    const res = await api.post('/api/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    const { access_token } = res.data;
    setToken(access_token);
    setTokenState(access_token);
    const meRes = await api.get('/api/auth/me');
    setUser(meRes.data);
    return meRes.data;
  }, []);

  const register = useCallback(async ({ email, password, full_name, role = 'driver' }) => {
    const res = await api.post('/api/auth/register', { email, password, full_name, role });
    const { access_token } = res.data;
    setToken(access_token);
    setTokenState(access_token);
    const meRes = await api.get('/api/auth/me');
    setUser(meRes.data);
    return meRes.data;
  }, []);

  const logout = useCallback(() => {
    removeToken();
    setTokenState(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
