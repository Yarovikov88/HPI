import { NavLink, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import styles from './Header.module.css';
import { useMediaQuery } from '../hooks/useMediaQuery';
import { useState, useEffect, useRef } from 'react';
import { MobileMenu } from './MobileMenu';
import defaultAvatar from '../assets/profile.jpg';
import gearHelpIcon from '../assets/gear-help-icon.png';

const Header: React.FC = () => {
  const { isAuthenticated, user, loading } = useAuth();
  const isMobile = useMediaQuery('(max-width: 768px)');
  const [isMenuOpen, setMenuOpen] = useState(false);
  const [showHelpMenu, setShowHelpMenu] = useState(false);
  const location = useLocation();
  const helpMenuRef = useRef<HTMLDivElement>(null);

  const avatarSrc = user?.avatar_url;
  const logoLink = isAuthenticated ? "/account/diagnostics" : "/";
  const onAuthPage = location.pathname === '/login' || location.pathname === '/signup';
  const isHomePage = location.pathname === '/';
  
  // Упрощенный Header для мобильной главной страницы И для страниц входа/регистрации
  const shouldShowSimplifiedHeader = (isMobile && isHomePage) || onAuthPage;

  const handleSupportClick = () => {
    if (!isAuthenticated) {
      window.location.href = 'mailto:support@hpi.expert';
    } else {
      window.open('https://dzen.ru/hpi', '_blank', 'noopener,noreferrer');
    }
  };

  // Обработчики для скрытия меню
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (helpMenuRef.current && !helpMenuRef.current.contains(event.target as Node)) {
        setShowHelpMenu(false);
      }
    };

    const handleScroll = () => {
      setShowHelpMenu(false);
    };

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setShowHelpMenu(false);
      }
    };

    if (showHelpMenu) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('scroll', handleScroll, true);
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('scroll', handleScroll, true);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [showHelpMenu]);

  return (
    <>
      <header className={styles.header}>
        <div className={styles.headerContainer}>
          <Link to={logoLink} className={styles.logo} aria-label="На главную">
            <div className={styles.logoText}>
              HPI<span className={styles.logoExpert}>.EXPERT</span>
            </div>
          </Link>
          
          <div className={styles.controls}>
            {!loading && (
              <>
                {isAuthenticated && !onAuthPage ? (
                  <>
                    <div className={styles.profileContainer}>
                      <button 
                        className={styles.helpButton}
                        onClick={() => setShowHelpMenu(!showHelpMenu)}
                        title="Меню помощи"
                      >
                        <img 
                          src={gearHelpIcon} 
                          alt="Помощь" 
                          className={styles.helpIcon}
                        />
                      </button>
                      {showHelpMenu && (
                        <div ref={helpMenuRef} className={styles.helpMenu}>
                          <div className={styles.helpMenuItem}>
                            Жалобы и предложения по работе сайта принимаем на <a href="mailto:support@hpi.expert">support@hpi.expert</a>
                          </div>
                        </div>
                      )}
                      <Link to="/account/profile" className={styles.profileLink}>
                        <img
                          src={avatarSrc || defaultAvatar}
                          alt="Профиль"
                          className={styles.profileAvatar}
                          onError={(e) => {
                            (e.target as HTMLImageElement).onerror = null;
                            (e.target as HTMLImageElement).src = defaultAvatar;
                          }}
                        />
                      </Link>
                    </div>
                  </>
                ) : (
                  // Упрощенная версия для мобильной главной страницы И страниц входа/регистрации
                  shouldShowSimplifiedHeader ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', position: 'relative' }}>
                      <button 
                        className={styles.helpButton}
                        onClick={() => setShowHelpMenu(!showHelpMenu)}
                        title="Поддержка"
                        aria-label="Поддержка"
                      >
                        <img 
                          src={gearHelpIcon} 
                          alt="Поддержка" 
                          className={styles.helpIcon}
                        />
                      </button>
                      {showHelpMenu && (
                        <div ref={helpMenuRef} className={styles.helpMenu}>
                          <div className={styles.helpMenuItem}>
                            Жалобы и предложения по работе сайта принимаем на <a href="mailto:support@hpi.expert">support@hpi.expert</a>
                          </div>
                        </div>
                      )}
                      <Link to="/login" className={styles.loginButton}>
                        Войти
                      </Link>
                    </div>
                  ) : (
                    // Полная версия для десктопа и других страниц
                    <>
                      <nav className={styles.nav}>
                        <NavLink to="/features" className={({ isActive }) => isActive ? `${styles.navLink} ${styles.activeLink}` : styles.navLink}>
                          Возможности
                        </NavLink>
                        <NavLink to="/pricing" className={({ isActive }) => isActive ? `${styles.navLink} ${styles.activeLink}` : styles.navLink}>
                          Тарифы
                        </NavLink>
                      </nav>
                      <button 
                        className={styles.helpButton}
                        onClick={() => setShowHelpMenu(!showHelpMenu)}
                        title="Поддержка"
                      >
                        <img 
                          src={gearHelpIcon} 
                          alt="Поддержка" 
                          className={styles.helpIcon}
                        />
                      </button>
                      {showHelpMenu && (
                        <div ref={helpMenuRef} className={styles.helpMenu}>
                          <div className={styles.helpMenuItem}>
                            Жалобы и предложения по работе сайта принимаем на <a href="mailto:support@hpi.expert">support@hpi.expert</a>
                          </div>
                        </div>
                      )}
                      <Link to="/login" className={styles.loginButton}>
                        Войти
                      </Link>
                    </>
                  )
                )}
              </>
            )}
          </div>
        </div>
      </header>
      {isMobile && <MobileMenu isOpen={isMenuOpen} onClose={() => setMenuOpen(false)} />}
    </>
  );
};

export default Header;
