import { NavLink, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import styles from './Header.module.css';
import logoUrl from '../assets/logo.svg';

const Header: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/'); // Перенаправляем на главную после выхода
  };

  return (
    <header className={styles.siteHeader}>
      <Link to="/" className={styles.logo} aria-label="На главную">
        <img src={logoUrl} alt="Логотип HPI.expert" width="44" height="44" />
      </Link>
      
      {!isAuthenticated && (
      <nav className={styles.headerNav}>
        <NavLink
          to="/features"
          className={({ isActive }) =>
            isActive ? `${styles.headerLink} ${styles.activeLink}` : styles.headerLink
          }
        >
          Возможности
        </NavLink>
        <NavLink
          to="/pricing"
          className={({ isActive }) =>
            isActive ? `${styles.headerLink} ${styles.activeLink}` : styles.headerLink
          }
        >
          Тарифы
          </NavLink>
        <NavLink
          to="/business"
          className={({ isActive }) =>
            isActive ? `${styles.headerLink} ${styles.activeLink}` : styles.headerLink
          }
        >
          Для бизнеса
          </NavLink>
        </nav>
      )}

      <div className={styles.headerActions}>
        {isAuthenticated ? (
          <div className={styles.userMenu}>
            <Link to="/account/profile" className={styles.avatarLink}>
              <img src="/src/assets/profile.jpg" alt="Профиль" className={styles.avatar} />
            </Link>
          </div>
        ) : (
          <Link to="/login" className={styles.loginButton}>
            Войти
          </Link>
        )}
      </div>
    </header>
  );
};

export default Header; 