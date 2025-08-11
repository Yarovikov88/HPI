import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';
import styles from './LoginPage.module.css';
import { apiClient } from '../services/api';

export default function LoginPage() {
  const { refreshProfile } = useAuth();
  const navigate = useNavigate();
  const [emailOrUsername, setEmailOrUsername] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      // Немедленный вход как user id=1 через dev-эндпоинт
      await apiClient.telegramAuth();
      await refreshProfile();
      navigate('/account/profile');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <Helmet>
        <title>Вход — HPI.expert</title>
        <meta name="description" content="Войдите в свой личный кабинет HPI.expert, чтобы получить доступ к опросам, дашбордам и персональным рекомендациям." />
      </Helmet>
      <div className={styles.container}>
        <h1>Вход в личный кабинет</h1>
        <form onSubmit={handleSubmit} className={styles.form}>
          <label>
            Email или логин
            <input
              type="text"
              value={emailOrUsername}
              onChange={(e) => setEmailOrUsername(e.target.value)}
            />
          </label>
          <label>
            Пароль
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
          <button type="submit" className={styles.telegramButton} disabled={submitting}>
            {submitting ? 'Входим…' : 'Войти'}
          </button>
        </form>
        <div className={styles.buttonGroup}>
          <Link to="/signup" className={styles.emailButton}>Создать аккаунт</Link>
        </div>
      </div>
    </>
  );
}
