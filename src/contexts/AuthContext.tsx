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
  updateUser: (data: Partial<UserProfile>) => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      try {
        console.log('🔄 AuthContext: Инициализация аутентификации');
        setLoading(true);
        
        const token = localStorage.getItem('authToken');
        if (token) {
          console.log(' AuthContext: Токен найден, загружаем профиль');
          await refreshProfile();
        } else {
          console.log(' AuthContext: Токен не найден');
        }
      } catch (error) {
        console.error('❌ AuthContext: Ошибка инициализации:', error);
      } finally {
        console.log('🔄 AuthContext: Устанавливаем loading = false');
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const refreshProfile = async () => {
    try {
      const profile = await apiClient.getProfile();
      setUser(profile);
    } catch {
      setUser(null);
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

  const updateUser = (data: Partial<UserProfile>) => {
    setUser(currentUser => currentUser ? { ...currentUser, ...data } : null);
  };

  const isAuthenticated = !loading && !!user;

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, loading, login, register, logout, refreshProfile, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}; 