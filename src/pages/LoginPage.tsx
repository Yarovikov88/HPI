import React from 'react';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import styles from './LoginPage.module.css';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = () => {
    // Имитируем вход пользователя "Иванов Иван"
    const mockUser = {
      id: '179', // Используем ID тестового пользователя
      full_name: 'Иванов Иван',
      email: 'ivanov@example.com',
    };
    login(mockUser);
    navigate('/account/profile'); 
  };

  return (
    <>
      <Helmet>
        <title>Вход — HPI.expert</title>
        <meta name="description" content="Войдите в свой личный кабинет HPI.expert, чтобы получить доступ к опросам, дашбордам и персональным рекомендациям." />
      </Helmet>
      <div className={styles.container}>
        <h1>Вход в личный кабинет</h1>
        <p>Для доступа к опросам и результатам, пожалуйста, войдите.</p>
        <div className={styles.buttonGroup}>
          <button onClick={handleLogin} className={styles.telegramButton}>
            Войти через Telegram
          </button>
          <button onClick={handleLogin} className={styles.emailButton}>
            Войти через Email
          </button>
        </div>
      </div>
    </>
  );
}
