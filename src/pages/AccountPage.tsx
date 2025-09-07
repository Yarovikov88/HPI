import React, { useState, useEffect } from 'react';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../hooks/useAuth';
import styles from './AccountPage.module.css';
import { Navigate, useNavigate, useLocation, Link } from 'react-router-dom';
import { apiClient } from '../services/api';
import { toast } from 'react-toastify';
import defaultAvatar from '../assets/profile.jpg';

const AccountPage: React.FC = () => {
  const { user, loading, logout, refreshProfile, updateUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { state } = location;
  const [notification, setNotification] = useState(state?.message || null);

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [telegram, setTelegram] = useState('');
  const [saving, setSaving] = useState(false);
  const [phoneError, setPhoneError] = useState<string | null>(null);
  const [showPwdModal, setShowPwdModal] = useState(false);
  const [oldPwd, setOldPwd] = useState('');
  const [newPwd, setNewPwd] = useState('');
  const [newPwd2, setNewPwd2] = useState('');
  const [changingPwd, setChangingPwd] = useState(false);
  const [proLoading, setProLoading] = useState(false);

  const isValidPhoneE164 = (value: string): boolean => {
    if (!value) return true;
    return /^\+[1-9]\d{7,14}$/.test(value);
  };

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setEmail(user.email || '');
      setPhone(user.phone || '');
      setTelegram(user.username || '');
    }
  }, [user]);

  useEffect(() => {
    if (notification) {
      window.history.replaceState({}, document.title);
    }
  }, [notification]);

  const handleSave = async () => {
    if (phone && !isValidPhoneE164(phone)) {
      setPhoneError('Неверный формат телефона. Используйте формат: +79990000000');
      return;
    }

    setPhoneError(null);
    setSaving(true);

    try {
      const updateData: any = {
        full_name: fullName,
        phone: phone || null,
        username: telegram || null,
      };

      await apiClient.put('/auth/profile', updateData);
      await refreshProfile();
      toast.success('Профиль обновлен');
    } catch (error: any) {
      console.error('Ошибка обновления профиля:', error);
      toast.error(error.response?.data?.detail || 'Ошибка обновления профиля');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Ошибка выхода:', error);
    }
  };

  const handleChangePassword = async () => {
    if (newPwd !== newPwd2) {
      toast.error('Пароли не совпадают');
      return;
    }

    if (newPwd.length < 6) {
      toast.error('Пароль должен содержать минимум 6 символов');
      return;
    }

    setChangingPwd(true);

    try {
      const data: any = { new_password: newPwd };
      if (user?.has_password) {
        data.old_password = oldPwd;
      }

      await apiClient.put('/auth/change-password', data);
      toast.success('Пароль изменен');
      setShowPwdModal(false);
      setOldPwd('');
      setNewPwd('');
      setNewPwd2('');
    } catch (error: any) {
      console.error('Ошибка смены пароля:', error);
      toast.error(error.response?.data?.detail || 'Ошибка смены пароля');
    } finally {
      setChangingPwd(false);
    }
  };

  if (loading) {
    return <div>Загрузка...</div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return (
    <>
      <Helmet>
        <title>Профиль — HPI.expert</title>
        <meta name="description" content="Управление профилем пользователя HPI.expert" />
      </Helmet>
      <div className={styles.container}>
        <div className={styles.profileCard}>
          <div className={styles.avatarSection}>
            <img
              src={user.avatar_url || defaultAvatar}
              alt="Аватар"
              className={styles.avatar}
              onError={(e) => {
                (e.target as HTMLImageElement).onerror = null;
                (e.target as HTMLImageElement).src = defaultAvatar;
              }}
            />
            <div className={styles.userInfo}>
              <h1 className={styles.userName}>{user.full_name || 'Пользователь'}</h1>
              <p className={styles.userEmail}>{user.email}</p>
            </div>
          </div>

          <div className={styles.formSection}>
            <div className={styles.field}>
              <label>Имя:</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
            <div className={styles.field}>
              <label>Email:</label>
              <input
                type="email"
                value={email}
                disabled
                className={styles.disabledInput}
              />
            </div>
            <div className={styles.field}>
              <label>Телефон:</label>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                pattern="^\\+[1-9]\\d{7,14}$"
                title="Формат: +79990000000"
              />
              {phone && phoneError && (
                <div style={{ color: '#d33', fontSize: 12, marginTop: 4 }}>{phoneError}</div>
              )}
            </div>
            <div className={styles.field}>
              <label>Telegram:</label>
              <input
                type="text"
                placeholder="@username"
                value={telegram}
                onChange={(e) => setTelegram(e.target.value)}
              />
            </div>
            <div className={styles.buttonContainer}>
              <div className={styles.buttonRow}>
                <button onClick={() => setShowPwdModal(true)} className={styles.changePwdButton}>
                  {user?.has_password ? 'Изменить пароль' : 'Установить пароль'}
                </button>
              </div>
              <div style={{ flex: 1 }} />
              <button onClick={handleSave} className={styles.saveButton} disabled={saving || (!!phone && !!phoneError)}>
                {saving ? 'Сохраняем…' : 'Сохранить изменения'}
              </button>
              <button onClick={handleLogout} className={styles.logoutButton}>Выйти</button>
            </div>
          </div>
        </div>

        {/* Версия внизу страницы */}
        <div className={styles.versionSection}>
          <div className={styles.versionTitle}>HPI.EXPERT</div>
          <div className={styles.versionNumber}>v.0.9.1</div>
        </div>

        {showPwdModal && (
          <div className={styles.modalBackdrop} onClick={() => !changingPwd && setShowPwdModal(false)}>
            <div className={styles.modalCard} onClick={(e) => e.stopPropagation()}>
              <h3 className={styles.modalTitle}>{user?.has_password ? 'Изменить пароль' : 'Установить пароль'}</h3>
              <div className={styles.modalForm}>
                <div className={styles.modalField}>
                  <label className={styles.modalLabel}>
                    {user?.has_password ? 'Текущий пароль' : 'Текущий пароль (не требуется)'}
                  </label>
                  <input className={styles.modalInput} type="password" value={oldPwd} onChange={(e) => setOldPwd(e.target.value)} />
                </div>
                <div className={styles.modalField}>
                  <label className={styles.modalLabel}>Новый пароль</label>
                  <input className={styles.modalInput} type="password" value={newPwd} onChange={(e) => setNewPwd(e.target.value)} />
                </div>
                <div className={styles.modalField}>
                  <label className={styles.modalLabel}>Повторите новый пароль</label>
                  <input className={styles.modalInput} type="password" value={newPwd2} onChange={(e) => setNewPwd2(e.target.value)} />
                </div>
                <div className={styles.modalActions}>
                  <button className={styles.modalSecondary} onClick={() => setShowPwdModal(false)} disabled={changingPwd}>Отмена</button>
                  <button className={styles.modalPrimary} onClick={handleChangePassword} disabled={changingPwd}>
                    {changingPwd ? 'Сохраняем…' : (user?.has_password ? 'Сменить пароль' : 'Установить пароль')}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default AccountPage; 