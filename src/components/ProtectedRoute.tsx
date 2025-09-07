import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useSurvey } from '../hooks/useSurvey';

interface ProtectedRouteProps {
  children: React.ReactNode;
  pro?: boolean;
}

const ProtectedRoute = ({ children, pro = false }: ProtectedRouteProps) => {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const { isBasicSurveyComplete, isProSurveyComplete, loading: surveyLoading } = useSurvey();
  const location = useLocation();

  const loading = authLoading || surveyLoading;

  if (loading) {
    return null; // или <LoadingSpinner />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Логика доступа к дашбордам
  const { pathname } = location;

  // Отладочная информация
  console.log('ProtectedRoute Debug:', {
    pathname,
    pro,
    isBasicSurveyComplete,
    isProSurveyComplete,
    userIsPro: user?.is_pro
  });

  // Если пользователь пытается зайти на базовый дашборд, не пройдя базовый опрос
  if (pathname.includes('/dashboard') && !pathname.includes('/pro-dashboard') && !isBasicSurveyComplete) {
    console.log('Redirecting to diagnostics: basic dashboard without basic survey');
    return <Navigate to="/account/diagnostics" replace state={{ message: 'Для доступа к дашборду необходимо завершить базовую диагностику.' }} />;
  }

  // Если пользователь пытается зайти на PRO дашборд, не пройдя PRO опрос
  if (pathname.includes('/pro-dashboard') && !isProSurveyComplete) {
    console.log('Redirecting to diagnostics: pro dashboard without pro survey');
    return <Navigate to="/account/diagnostics" replace state={{ message: 'Для доступа к PRO дашборду необходимо завершить PRO диагностику.' }} />;
  }
  
  // Новая логика: если роут требует PRO, а у пользователя его нет
  if (pro && !user?.is_pro) {
    console.log('Redirecting to profile: pro route without pro user');
    // Перенаправляем на страницу профиля с сообщением
    return <Navigate to="/account/profile" replace state={{ message: 'Эта страница доступна только для PRO-пользователей.' }} />;
  }

  return <>{children}</>;
};

export default ProtectedRoute; 