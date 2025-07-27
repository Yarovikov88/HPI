import React from 'react';
import { useAuth } from '../hooks/useAuth';
import styles from './AccountPage.module.css';
import { Navigate } from 'react-router-dom';

const AccountPage: React.FC = () => {
  const { user, loading, logout } = useAuth();

  if (loading) {
    return <div>Загрузка...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const handleLogout = () => {
    logout();
    // Optionally, redirect to login page after logout
    window.location.href = '/login';
  };

  return (
    <div className={styles.accountContainer}>
      <div className={styles.profileHeader}>
        <img src="/src/assets/profile.jpg" alt="Аватар" className={styles.avatar} />
        <h1 className={styles.userName}>{user.full_name || 'Пользователь'}</h1>
      </div>
      <div className={styles.card}>
        <div className={styles.field}>
          <label>ID пользователя:</label>
          <span className={styles.userId}>{user.id}</span>
        </div>
        <div className={styles.field}>
          <label>ФИО:</label>
          <input type="text" defaultValue={user.full_name || ''} />
        </div>
        <div className={styles.field}>
          <label>Email:</label>
          <input type="email" defaultValue={user.email} />
        </div>
        <div className={styles.field}>
          <label>Телефон:</label>
          <input type="tel" defaultValue={user.phone || ''} />
        </div>
        <div className={styles.field}>
          <label>Telegram:</label>
          <input type="text" defaultValue={user.telegram || ''} />
        </div>
        <div className={styles.buttonContainer}>
          <button className={styles.saveButton}>Сохранить изменения</button>
          <button onClick={handleLogout} className={styles.logoutButton}>Выйти</button>
        </div>
      </div>
    </div>
  );
};

export default AccountPage; 