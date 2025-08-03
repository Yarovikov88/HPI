import { NavLink, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import styles from './Header.module.css';

const Header: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/'); // Перенаправляем на главную после выхода
  };

  return (
    <header className={styles.header}>
      <div className={styles.headerContainer}>
        <Link to="/" className={styles.logo} aria-label="На главную">
          <div className={styles.logoText}>
            HPI<span className={styles.logoExpert}>.EXPERT</span>
          </div>
        </Link>
        {!isAuthenticated && (
          <nav className={styles.nav}>
            <NavLink
              to="/features"
              className={({ isActive }) =>
                isActive ? `${styles.navLink} ${styles.activeLink}` : styles.navLink
              }
            >
              Возможности
            </NavLink>
            <NavLink
              to="/pricing"
              className={({ isActive }) =>
                isActive ? `${styles.navLink} ${styles.activeLink}` : styles.navLink
              }
            >
              Тарифы
            </NavLink>
            <NavLink
              to="/business"
              className={({ isActive }) =>
                isActive ? `${styles.navLink} ${styles.activeLink}` : styles.navLink
              }
            >
              Для бизнеса
            </NavLink>
          </nav>
        )}
        <div className={styles.controls}>
          {isAuthenticated ? null : (
            <Link to="/login" className={styles.loginButton}>
              Войти
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header; 