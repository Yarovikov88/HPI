import React, { createContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { apiClient, type UserProfile, type UserLogin, type UserRegister } from '../services/api';

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (credentials: UserLogin) => Promise<void>;
  register: (data: UserRegister) => Promise<void>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      try {
        let token = localStorage.getItem('authToken');
        if (!token) {
          // Автовход через Telegram-авторизацию (dev/стаб)
          token = await apiClient.telegramAuth();
        }
        if (token) {
          try {
            const profile = await apiClient.getProfile();
            setUser(profile);
          } catch {
            // Фоллбэк: если профиль не доступен, но токен есть — используем заглушку id=1
            setUser({ id: 1, full_name: 'User One' });
          }
        } else {
          setUser(null);
        }
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  const refreshProfile = async () => {
    try {
      const profile = await apiClient.getProfile();
      setUser(profile);
    } catch {
      const token = localStorage.getItem('authToken');
      if (token) {
        setUser({ id: 1, full_name: 'User One' });
      } else {
        setUser(null);
      }
    }
  };

  const login = async (credentials: UserLogin) => {
    await apiClient.login(credentials);
    await refreshProfile();
  };

  const register = async (data: UserRegister) => {
    await apiClient.register(data);
    await refreshProfile();
  };

  const logout = () => {
    apiClient.logout();
    setUser(null);
  };

  const isAuthenticated = !loading && !!user;

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, loading, login, register, logout, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  );
}; 