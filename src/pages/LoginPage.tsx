import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';
import styles from './LoginPage.module.css';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await login({ email, password });
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
        <h1 className={styles.title}>Вход в личный кабинет</h1>
        <p className={styles.subtitle}>Продолжите, чтобы получить доступ к диагностике и дашбордам.</p>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label}>
              Email
            </label>
            <input
              className={styles.input}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>
              Пароль
            </label>
            <input
              className={styles.input}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className={styles.submitButton} disabled={submitting}>
            {submitting ? 'Входим…' : 'Войти'}
          </button>
        </form>
        <div className={styles.footer}>
          Нет аккаунта? <Link to="/signup" className={styles.link}>Зарегистрироваться</Link>
        </div>
      </div>
    </>
  );
}
