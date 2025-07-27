import React from 'react';
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
  );
}
