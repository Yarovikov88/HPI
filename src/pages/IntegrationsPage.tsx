import styles from './Page.module.css';
import { Link } from 'react-router-dom';

const integrations = [
  { title: 'Календари', services: 'Google Calendar, Apple Calendar' },
  { title: 'Таск-менеджеры', services: 'Todoist, Trello, Asana' },
  { title: 'Здоровье и фитнес', services: 'Apple Health, Google Fit, Strava' },
  { title: 'Заметки и знания', services: 'Notion, Obsidian, Evernote' },
  { title: 'Код и разработка', services: 'GitHub, GitLab' },
];

export default function IntegrationsPage() {
  return (
    <div className={styles.page}>
      <h1>Интеграции (скоро)</h1>
      <p style={{ fontSize: '1.2rem', color: 'var(--text-color-primary)', marginBottom: 32 }}>
        Сделайте HPI.EXPERT центром своей цифровой экосистемы. В будущем вы сможете подключать сторонние сервисы, чтобы автоматически собирать данные о вашей активности, экономить время на ручном вводе и получать полную, объективную картину вашей жизни.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 24, marginBottom: 40 }}>
        {integrations.map((item, idx) => (
          <div key={idx} style={{ border: '1px solid #e0e0e0', borderRadius: 16, padding: 24, background: '#fff', boxShadow: '0 4px 12px rgba(10,36,99,0.06)' }}>
            <h3 style={{ color: 'var(--primary-brand-color)', marginTop: 0, marginBottom: 12 }}>{item.title}</h3>
            <p style={{ color: 'var(--text-color-primary)', marginBottom: 0 }}>{item.services}</p>
          </div>
        ))}
      </div>
      <div className={styles.centeredSection}>
        <h2>Интеграции появятся в ближайших обновлениях!</h2>
        <Link to="/signup" className={`${styles.ctaButton} ${styles.disabled}`}>
          Начать бесплатно (Скоро)
        </Link>
        <p className={styles.subtleText}>
          Раздел находится в разработке. Следите за обновлениями!
        </p>
      </div>
    </div>
  );
} 