import styles from './Footer.module.css';

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.footerIcons}>
        <a href="mailto:88@robius.ru" aria-label="Email"><i className="icon-mail"></i></a>
        <a href="https://t.me/hpi_expert" target="_blank" rel="noopener noreferrer" aria-label="Telegram"><i className="icon-telegram"></i></a>
        <a href="https://www.linkedin.com/company/hpi-expert/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn"><i className="icon-linkedin"></i></a>
      </div>
      <div className={styles.footerCopyright}>
        © 2025 HPI.EXPERT<br />
        Разработано <a href="https://robius.ru" target="_blank" rel="noopener noreferrer">ROBIUS IT</a>
      </div>
    </footer>
  );
} 