import { Link } from 'react-router-dom';
import styles from './FeaturesIndexPage.module.css';
import pageStyles from '../Page.module.css';

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
        <Link to="/signup" className={`${pageStyles.btn} ${pageStyles.btnPrimary}`}>Начать бесплатно</Link>
      </div>
    </>
  );
} 