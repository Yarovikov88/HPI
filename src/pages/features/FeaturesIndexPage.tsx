import { Link } from 'react-router-dom';
import styles from './FeaturesIndexPage.module.css';

const features = [
  {
    path: '/features/dashboard',
    title: 'Интерактивный дашборд',
    description: 'Вся аналитика по вашему развитию в одном месте. Отслеживайте HPI, ключевые метрики и прогресс по целям.',
  },
  {
    path: '/features/ai',
    title: 'Персональные AI-рекомендации',
    description: 'Получайте советы от искусственного интеллекта, основанные на ваших данных, для принятия эффективных решений.',
  },
  {
    path: '/features/goals',
    title: 'Цели и трекинг',
    description: 'Ставьте амбициозные цели, разбивайте их на шаги и отслеживайте достижение в реальном времени.',
  },
];

export default function FeaturesIndexPage() {
  return (
    <>
      <div className={styles.featuresList}>
        {features.map((feature) => (
          <Link to={feature.path} key={feature.path} className={styles.featureCard}>
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
          </Link>
        ))}
      </div>
      <div style={{ textAlign: 'center', marginTop: 48 }}>
        <h2 style={{ color: 'var(--primary-brand-color)', fontSize: '2rem', fontWeight: 600, marginBottom: 16 }}>
          Присоединяйтесь к HPI.expert и начните свой путь развития!
        </h2>
        <p style={{ color: 'var(--text-color-primary)', fontSize: '1.1rem', marginBottom: 32 }}>
          Получите доступ к персональной аналитике, AI-рекомендациям и инструментам для достижения ваших целей.
        </p>
        <Link to="/signup" style={{
          display: 'inline-block',
          background: 'var(--cta-brand-color)',
          color: '#fff',
          border: 'none',
          borderRadius: 8,
          fontSize: 16,
          height: 40,
          padding: '0 32px',
          cursor: 'pointer',
          fontWeight: 500,
          textDecoration: 'none',
          transition: 'background 0.2s, box-shadow 0.2s',
          boxShadow: '0 2px 8px rgba(255,77,79,0.15)'
        }}>
          Начать бесплатно
        </Link>
      </div>
    </>
  );
} 