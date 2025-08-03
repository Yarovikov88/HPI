import React from 'react';
import { Helmet } from 'react-helmet-async';
import styles from '../Page.module.css';
import buttonStyles from '../../components/Button.module.css';
import { Link } from 'react-router-dom';

const aiBenefits = [
  {
    title: 'Персонализированные советы',
    description: 'AI анализирует ваши данные и предлагает индивидуальные рекомендации для развития и достижения целей.'
  },
  {
    title: 'Автоматический анализ прогресса',
    description: 'Система отслеживает ваши успехи и подсказывает, где можно улучшить результат.'
  },
  {
    title: 'Мотивация и поддержка',
    description: 'AI напоминает о целях, мотивирует и помогает не сбиться с пути.'
  },
  {
    title: 'Безопасность и приватность',
    description: 'Ваши данные защищены и используются только для персонализации рекомендаций.'
  }
];

const AiFeaturePage = () => {
  return (
    <>
      <Helmet>
        <title>Персональные AI-рекомендации — HPI.expert</title>
        <meta name="description" content="Получайте советы от искусственного интеллекта, основанные на ваших данных, для принятия эффективных решений и ускорения вашего роста." />
      </Helmet>
      <div className={styles.page}>
        <h1>Персональные AI-рекомендации</h1>
        <p style={{ fontSize: '1.2rem', color: 'var(--text-color-primary)', marginBottom: 32 }}>
          Искусственный интеллект HPI.expert помогает вам принимать решения, достигать целей и развиваться быстрее благодаря персонализированным советам и анализу ваших данных.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 24, marginBottom: 40 }}>
          {aiBenefits.map((item, idx) => (
            <div key={idx} style={{ border: '1px solid #e0e0e0', borderRadius: 16, padding: 24, background: '#fff', boxShadow: '0 4px 12px rgba(10,36,99,0.06)' }}>
              <h3 style={{ color: 'var(--primary-brand-color)', marginTop: 0, marginBottom: 12 }}>{item.title}</h3>
              <p style={{ color: 'var(--text-color-primary)', marginBottom: 0 }}>{item.description}</p>
            </div>
          ))}
        </div>
        <div style={{ textAlign: 'center', marginTop: 32 }}>
          <h2 style={{ color: 'var(--primary-brand-color)', fontSize: '1.5rem', fontWeight: 600, marginBottom: 16 }}>
            Попробуйте AI-рекомендации бесплатно!
          </h2>
          <Link to="/signup" className={buttonStyles.ctaButton}>
            Начать бесплатно
          </Link>
        </div>
      </div>
    </>
  );
};

export default AiFeaturePage; 