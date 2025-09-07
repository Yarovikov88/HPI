import { useNavigate } from 'react-router-dom';
import SocialIcon from './SocialIcon';
import { useState } from 'react';
import { useMediaQuery } from '../hooks/useMediaQuery';
import styles from './Footer.module.css';

export default function Footer() {
  const isMobile = useMediaQuery('(max-width: 768px)');
  const navigate = useNavigate();

  const [openNav, setOpenNav] = useState<boolean>(false);
  const [openResources, setOpenResources] = useState<boolean>(false);

  const handleLinkClick = (path: string) => {
    navigate(path);
  };

  const handleExternalLinkClick = (url: string) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  return (
    <footer className={styles.footer}>
      <div className={styles.footerContent}>
        {!isMobile && (
          <div className={styles.footerBrand}>
            <h3 className={styles.footerLogo}>HPI.EXPERT</h3>
            <p>Платформа для оценки и развития вашего человеческого потенциала</p>
            <address>
              <span 
                className={styles.emailLink}
                onClick={() => handleExternalLinkClick('mailto:expert@hpi.expert')}
              >
                expert@hpi.expert
              </span>
            </address>
          </div>
        )}

        {isMobile ? (
          <div className={styles.accordion}>
            <div className={styles.accordionItem}>
              <button className={styles.accordionHeader} onClick={() => setOpenNav((v) => !v)} aria-expanded={openNav}>
                <span className={styles.accordionTitle}>Продукт</span>
                <span className={`${styles.chevron} ${openNav ? styles.open : ''}`}></span>
              </button>
              {openNav && (
                <div className={styles.accordionContent}>
                  <span 
                    className={styles.linkText}
                    onClick={() => handleLinkClick('/methodology')}
                  >
                    Методология
                  </span>
                  <span 
                    className={styles.linkText}
                    onClick={() => handleLinkClick('/features')}
                  >
                    Возможности
                  </span>
                  <span 
                    className={styles.linkText}
                    onClick={() => handleLinkClick('/business')}
                  >
                    Для бизнеса
                  </span>
                </div>
              )}
            </div>

            <div className={styles.accordionItem}>
              <button className={styles.accordionHeader} onClick={() => setOpenResources((v) => !v)} aria-expanded={openResources}>
                <span className={styles.accordionTitle}>Ресурсы</span>
                <span className={`${styles.chevron} ${openResources ? styles.open : ''}`}></span>
              </button>
              {openResources && (
                <div className={styles.accordionContent}>
                  <span 
                    className={styles.linkText}
                    onClick={() => handleExternalLinkClick('https://vk.com/hpi_expert')}
                  >
                    Наша группа Вконтакте
                  </span>
                  <span 
                    className={styles.linkText}
                    onClick={() => handleExternalLinkClick('https://t.me/hpi_expert')}
                  >
                    Наш телеграм канал
                  </span>
                  <span 
                    className={styles.linkText}
                    onClick={() => handleExternalLinkClick('https://dzen.ru/hpi')}
                  >
                    Наша страница на Дзен
                  </span>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className={styles.footerLinks}>
            <div className={styles.linkColumn}>
              <h4>Продукт</h4>
              <span 
                className={styles.linkText}
                onClick={() => handleLinkClick('/methodology')}
              >
                Методология
              </span>
              <span 
                className={styles.linkText}
                onClick={() => handleLinkClick('/features')}
              >
                Возможности
              </span>
              <span 
                className={styles.linkText}
                onClick={() => handleLinkClick('/business')}
              >
                Для бизнеса
              </span>
            </div>
            <div className={styles.linkColumn}>
              <h4>Ресурсы</h4>
              <span 
                className={styles.linkText}
                onClick={() => handleExternalLinkClick('https://vk.com/hpi_expert')}
              >
                Наша группа Вконтакте
              </span>
              <span 
                className={styles.linkText}
                onClick={() => handleExternalLinkClick('https://t.me/hpi_expert')}
              >
                Наш телеграм канал
              </span>
              <span 
                className={styles.linkText}
                onClick={() => handleExternalLinkClick('https://dzen.ru/hpi')}
              >
                Наша страница на Дзен
              </span>
            </div>
          </div>
        )}
      </div>

      <div className={styles.footerBottom}>
        <p className={styles.copyright}>
          © {new Date().getFullYear()} HPI.EXPERT
          <span 
            className={styles.madeByLink}
            onClick={() => handleExternalLinkClick('https://robius-it.ru')}
          >
            {' '}Разработано <strong>ROBIUS IT</strong>
          </span>
        </p>
        <div className={styles.footerMeta}>
          <div className={styles.socials}>
            <span 
              className={styles.socialIcon}
              onClick={() => handleExternalLinkClick('https://vk.com/hpi_expert')}
              aria-label="VK"
            >
              <SocialIcon name="vk" />
            </span>
            <span 
              className={styles.socialIcon}
              onClick={() => handleExternalLinkClick('https://t.me/hpi_expert')}
              aria-label="Telegram"
            >
              <SocialIcon name="tg" />
            </span>
          </div>
          <span className={styles.language}>Русский </span>
        </div>
        <div className={styles.bottomLinks}>
          <span 
            className={styles.linkText}
            onClick={() => handleLinkClick('/terms')}
          >
            Условия использования
          </span>
          <span 
            className={styles.linkText}
            onClick={() => handleLinkClick('/privacy')}
          >
            Политика конфиденциальности
          </span>
          <span 
            className={styles.linkText}
            onClick={() => handleLinkClick('/cookies')}
          >
            Cookie
          </span>
          <span 
            className={styles.linkText}
            onClick={() => handleLinkClick('/recommendations')}
          >
            Рекомендательные технологии
          </span>
        </div>
      </div>
    </footer>
  );
}
