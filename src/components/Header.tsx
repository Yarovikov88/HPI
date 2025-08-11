import { NavLink, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import styles from './Header.module.css';
import profileImage from '../assets/profile.jpg'; // Импортируем изображение профиля

const Header: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <header className={styles.header}>
      <div className={styles.headerContainer}>
        <Link to="/" className={styles.logo} aria-label="На главную">
          <div className={styles.logoText}>
            HPI<span className={styles.logoExpert}>.EXPERT</span>
          </div>
        </Link>
        
        <div className={styles.controls}>
          {isAuthenticated ? (
            // --- Блок с круглым логотипом пользователя ---
            <Link to="/account/profile" className={styles.profileLink}>
              <img src={profileImage} alt="Профиль" className={styles.profileAvatar} />
            </Link>
          ) : (
            // --- Блок для неавторизованного пользователя ---
            <>
              <nav className={styles.nav}>
                <NavLink to="/features" className={({ isActive }) => isActive ? `${styles.navLink} ${styles.activeLink}` : styles.navLink}>
                  Возможности
                </NavLink>
                <NavLink to="/pricing" className={({ isActive }) => isActive ? `${styles.navLink} ${styles.activeLink}` : styles.navLink}>
                  Тарифы
                </NavLink>
                <NavLink to="/business" className={({ isActive }) => isActive ? `${styles.navLink} ${styles.activeLink}` : styles.navLink}>
                  Для бизнеса
                </NavLink>
              </nav>
              <Link to="/login" className={styles.loginButton}>
                Войти
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header; 