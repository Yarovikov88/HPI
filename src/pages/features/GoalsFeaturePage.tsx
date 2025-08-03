import React from 'react';
import { Helmet } from 'react-helmet-async';
import styles from '../Page.module.css';
import buttonStyles from '../../components/Button.module.css';
import { Link } from 'react-router-dom';

const goalBenefits = [
  {
    title: 'Постановка амбициозных целей',
    description: 'Формулируйте личные и профессиональные цели, которые действительно важны для вас.'
  },
  {
    title: 'Разделение на шаги',
    description: 'Дробите большие задачи на понятные этапы и отслеживайте прогресс по каждому из них.'
  },
  {
    title: 'Визуализация и трекинг',
    description: 'Видьте свой путь к цели наглядно: диаграммы, прогресс-бары, напоминания.'
  },
  {
    title: 'Аналитика и поддержка',
    description: 'Получайте аналитику по достижению целей и персональные рекомендации для повышения эффективности.'
  }
];

const GoalsFeaturePage = () => {
  return (
    <>
      <Helmet>
        <title>Цели и трекинг — HPI.expert</title>
        <meta name="description" content="Ставьте амбициозные цели, разбивайте их на шаги и отслеживайте достижение в реальном времени. Системный подход к реализации ваших планов." />
      </Helmet>
      <div className={styles.page}>
        <h1>Цели и трекинг</h1>
        <p style={{ fontSize: '1.2rem', color: 'var(--text-color-primary)', marginBottom: 32 }}>
          Ставьте амбициозные цели, разбивайте их на шаги и отслеживайте прогресс в реальном времени. HPI.expert помогает реализовать ваши планы системно и эффективно.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 24, marginBottom: 40 }}>
          {goalBenefits.map((item, idx) => (
            <div key={idx} style={{ border: '1px solid #e0e0e0', borderRadius: 16, padding: 24, background: '#fff', boxShadow: '0 4px 12px rgba(10,36,99,0.06)' }}>
              <h3 style={{ color: 'var(--primary-brand-color)', marginTop: 0, marginBottom: 12 }}>{item.title}</h3>
              <p style={{ color: 'var(--text-color-primary)', marginBottom: 0 }}>{item.description}</p>
            </div>
          ))}
        </div>
        <div style={{ textAlign: 'center', marginTop: 32 }}>
          <h2 style={{ color: 'var(--primary-brand-color)', fontSize: '1.5rem', fontWeight: 600, marginBottom: 16 }}>
            Начните путь к своим целям уже сегодня!
          </h2>
          <Link to="/signup" className={buttonStyles.ctaButton}>
            Начать бесплатно
          </Link>
        </div>
      </div>
    </>
  );
};

export default GoalsFeaturePage; 