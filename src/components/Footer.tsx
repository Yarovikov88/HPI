import styles from './Footer.module.css';
import SocialIcon from './SocialIcon';

const Footer = () => {
  return (
    <footer className={styles.siteFooter}>
      <div className={styles.container}>
        <div className={styles.socialLinks}>
          <a href="https://t.me/yarovikov88" target="_blank" rel="noopener noreferrer" aria-label="Telegram">
            <SocialIcon name="tg" size={28} />
          </a>
          <a href="https://linkedin.com/in/yarovikov88" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
            <SocialIcon name="linkedin" size={28} />
          </a>
          <a href="mailto:yarovikov88@ya.ru" aria-label="Email">
            <SocialIcon name="email" size={28} />
          </a>
        </div>
        <div className={styles.footerInner}>
          <p className={styles.copyright}>© 2025 HPI.EXPERT</p>
          <p className={styles.developer}>
            Разработано <a href="https://robius-it.ru" target="_blank" rel="noopener noreferrer" className={styles.developerLink}>ROBIUS IT</a>
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 