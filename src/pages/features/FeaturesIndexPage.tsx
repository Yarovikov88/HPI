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
    <div className={styles.featuresList}>
      {features.map((feature) => (
        <Link to={feature.path} key={feature.path} className={styles.featureCard}>
          <h3>{feature.title}</h3>
          <p>{feature.description}</p>
        </Link>
      ))}
    </div>
  );
} 