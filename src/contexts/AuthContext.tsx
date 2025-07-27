import React, { createContext, useState, useContext, useEffect } from 'react';
import type { ReactNode } from 'react';

// Определяем структуру данных пользователя
interface User {
  id: string;
  email: string;
  full_name?: string;
  phone?: string;
  telegram?: string;
}

// Определяем, что будет храниться в контексте
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean; // Добавили состояние загрузки
  login: (userData: User) => void;
  logout: () => void;
}

// Создаем контекст с начальным значением undefined
export const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Создаем провайдер контекста
export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true); // Начальное состояние - загрузка

  useEffect(() => {
    // Имитация проверки аутентификации при запуске приложения
    const checkAuth = () => {
      try {
        // В реальном приложении здесь была бы проверка токена в localStorage
        // Для демонстрации, мы просто считаем, что пользователь "вошел в систему"
        // если в localStorage есть мок-данные.
        const mockUser = localStorage.getItem('mockUser');
        if (mockUser) {
          setUser(JSON.parse(mockUser));
        }
      } catch (error) {
        console.error("Ошибка при проверке аутентификации", error);
        setUser(null);
      } finally {
        setLoading(false); // Завершаем загрузку
      }
    };

    checkAuth();
  }, []);


  // Функция для "входа"
  const login = (userData: User) => {
    setUser(userData);
    localStorage.setItem('mockUser', JSON.stringify(userData));
  };

  // Функция для "выхода"
  const logout = () => {
    setUser(null);
    localStorage.removeItem('mockUser');
  };

  const isAuthenticated = !loading && !!user; // Аутентифицирован, только если загрузка не идет и есть юзер

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}; 