import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useSurvey } from '../hooks/useSurvey';
import styles from './MobileMenu.module.css';

interface MobileMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MobileMenu: React.FC<MobileMenuProps> = ({ isOpen, onClose }) => {
  const { user } = useAuth();
  const { isBasicSurveyComplete } = useSurvey();

  const handleDashboardClick = (e: React.MouseEvent) => {
    if (!isBasicSurveyComplete) {
      e.preventDefault();
      alert('Для доступа к дашборду необходимо завершить базовую диагностику.');
      onClose();
      return;
    }
    onClose();
  };

  return (
    <>
      <div className={`${styles.mobileMenu} ${isOpen ? styles.open : ''}`}>
        <div className={styles.menuHeader}>
          <h4>{user?.full_name || 'Меню'}</h4>
          <button onClick={onClose} className={styles.closeButton}>×</button>
        </div>
        <nav className={styles.mobileNav}>
          <NavLink
            to="/account/dashboard"
            onClick={handleDashboardClick}
            className={({ isActive }) => `${isActive ? styles.active : ''} ${!isBasicSurveyComplete ? styles.disabled : ''}`}
          >
            Дашборд
          </NavLink>
          <NavLink
            to="/account/diagnostics"
            onClick={onClose}
            className={({ isActive }) => isActive ? styles.active : ''}
          >
            Диагностика
          </NavLink>
          <NavLink
            to="/account/profile"
            onClick={onClose}
            className={({ isActive }) => isActive ? styles.active : ''}
          >
            Профиль
          </NavLink>
        </nav>
      </div>
      {isOpen && <div className={styles.overlay} onClick={onClose} />}
    </>
  );
}; 