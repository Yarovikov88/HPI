import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';
import styles from './LoginPage.module.css';

const SignupPage = () => {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await register({ email, password, first_name: firstName, last_name: lastName });
      navigate('/account/profile');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Создать аккаунт</h1>
      <p className={styles.subtitle}>Зарегистрируйтесь, чтобы начать диагностику и получать рекомендации.</p>
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.field}>
          <label className={styles.label}>Имя</label>
          <input className={styles.input} value={firstName} onChange={(e) => setFirstName(e.target.value)} />
        </div>
        <div className={styles.field}>
          <label className={styles.label}>Фамилия</label>
          <input className={styles.input} value={lastName} onChange={(e) => setLastName(e.target.value)} />
        </div>
        <div className={styles.field}>
          <label className={styles.label}>Email</label>
          <input className={styles.input} type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <div className={styles.field}>
          <label className={styles.label}>Пароль</label>
          <input className={styles.input} type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </div>
        <button type="submit" className={styles.submitButton} disabled={submitting}>
          {submitting ? 'Создаём…' : 'Зарегистрироваться'}
        </button>
      </form>
      <div className={styles.footer}>
        Уже есть аккаунт? <Link to="/login" className={styles.link}>Войти</Link>
      </div>
    </div>
  );
};

export default SignupPage; 