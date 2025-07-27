import React from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './DiagnosticsPage.module.css';

export default function DiagnosticsPage() {
  const navigate = useNavigate();

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  return (
    <div>
      <h2>Диагностика</h2>
      <p>Выберите опросник, который хотите пройти, чтобы оценить свой потенциал.</p>
      <div className={styles.diagnosticsContainer}>
        <div className={styles.surveyCard}>
          <h3>Базовая диагностика</h3>
          <p>Оцените свое состояние по 8 ключевым сферам жизни. Это займет не более 5 минут.</p>
          <button onClick={() => handleNavigation('/survey')} className={styles.ctaButton}>
            Начать
          </button>
        </div>
        <div className={styles.surveyCard}>
          <h3>Pro диагностика</h3>
          <p>Комплексная оценка по профессиональным методикам. Чтобы получить индивидуальные рекомендации с глубокой проработкой от AI, необходимо пройти Pro диагностику.</p>
          <button onClick={() => handleNavigation('/pro-survey')} className={styles.ctaButton}>
            Начать
          </button>
        </div>
      </div>
    </div>
  );
} 