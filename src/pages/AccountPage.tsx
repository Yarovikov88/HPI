import React, { useState, useEffect } from 'react';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../hooks/useAuth';
import styles from './AccountPage.module.css';
import { Navigate } from 'react-router-dom';
import { apiClient } from '../services/api';
import { toast } from 'react-toastify';

const AccountPage: React.FC = () => {
  const { user, loading, logout, refreshProfile } = useAuth();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [telegram, setTelegram] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setEmail(user.email || '');
      setPhone(user.phone || '');
      // telegram поле в API может отсутствовать — оставим локально как заметку пользователя
      setTelegram((user as any).telegram || '');
    }
  }, [user]);

  if (loading) {
    return <div>Загрузка...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Отправляем только поддерживаемые сервером поля
      await apiClient.updateProfile({ full_name: fullName, email, phone });
      await refreshProfile();
      toast.success('Профиль сохранен');
    } catch (e) {
      // Ошибка уже будет показана глобальным интерсептором, но добавим локальный фоллбэк
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <Helmet>
        <title>Мой профиль — HPI.expert</title>
      </Helmet>
      <div className={styles.accountContainer}>
        <div className={styles.profileHeader}>
          <img src="/src/assets/profile.jpg" alt="Аватар" className={styles.avatar} />
          <h1 className={styles.userName}>{fullName || 'Пользователь'}</h1>
        </div>
        <div className={styles.card}>
          <div className={styles.field}>
            <label>ID пользователя:</label>
            <input type="text" value={String(user.id)} disabled />
          </div>
          <div className={styles.field}>
            <label>ФИО:</label>
            <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </div>
          <div className={styles.field}>
            <label>Email:</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div className={styles.field}>
            <label>Телефон:</label>
            <input type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} />
          </div>
          <div className={styles.field}>
            <label>Telegram:</label>
            <input type="text" value={telegram} onChange={(e) => setTelegram(e.target.value)} />
          </div>
          <div className={styles.buttonContainer}>
            <button onClick={handleSave} className={styles.saveButton} disabled={saving}>
              {saving ? 'Сохраняем…' : 'Сохранить изменения'}
            </button>
            <button onClick={handleLogout} className={styles.logoutButton}>Выйти</button>
          </div>
        </div>
      </div>
    </>
  );
};

export default AccountPage; 