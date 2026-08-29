import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import authService from '../services/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // On mount, check if an Odoo session cookie is already valid (e.g.
  // page refresh) before forcing a fresh login.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const sessionUser = await authService.getSession();
        if (!cancelled) setUser(sessionUser);
      } catch {
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const login = useCallback(async (login_, password) => {
    setError(null);
    try {
      const loggedInUser = await authService.login(login_, password);
      setUser(loggedInUser);
      return loggedInUser;
    } catch (err) {
      setError(err.apiMessage || 'Login failed.');
      throw err;
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } finally {
      setUser(null);
    }
  }, []);

  const hasRole = useCallback(
    (role) => Boolean(user && user.roles && user.roles.includes(role)),
    [user]
  );

  return (
    <AuthContext.Provider value={{ user, loading, error, login, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
}
