import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import styles from '../Page.module.css';

const GoalsFeaturePage = () => {
  return (
    <>
      <Helmet>
        <title>Стратегические цели и трекинг — HPI.expert</title>
        <meta name="description" content="Ставьте цели, которые высвобождают ресурсы для роста. Отслеживайте, как достижение одной цели влияет на баланс всех сфер жизни." />
      </Helmet>
      <div className={styles.page}>
        <h1>Цели, которые высвобождают ресурсы для роста</h1>
        <p className={styles.subheadline}>
          Ставьте стратегические цели по сферам жизни и отслеживайте, как они влияют на общий баланс
        </p>

        <h4>Стратегические цели вместо хаотичных желаний</h4>
        <p>
          HPI.EXPERT помогает ставить цели, которые не просто достигаются, а высвобождают ресурсы для развития других сфер жизни. Это не просто планирование — это стратегическое управление своим потенциалом.
        </p>

        <div className={styles.contentSection}>
          <h4 className={styles.contentHeader}>Как ставить стратегические цели по сферам?</h4>
          <ul className={styles.contentList}>
            <li><strong>1. Анализ дисбаланса:</strong> Сначала понимаем, где у вас "узкие места".</li>
            <li><strong>2. Приоритизация сфер:</strong> Определяем, что развивать в первую очередь.</li>
            <li><strong>3. SMART-цели в контексте HPI:</strong> Конкретные, измеримые цели с привязкой к метрикам.</li>
            <li><strong>4. Корреляционный план:</strong> Как достижение одной цели повлияет на другие.</li>
            <li><strong>5. Ресурсное планирование:</strong> Сколько времени и энергии потребует каждая цель.</li>
          </ul>
        </div>

        <div className={styles.contentSection}>
          <h4 className={styles.contentHeader}>Примеры стратегических целей:</h4>
          <p>
            <strong>Обычная цель:</strong> "Хочу больше зарабатывать"
            <br />
            <strong>Стратегическая цель:</strong> "Увеличить доход на 30% за 6 месяцев через развитие навыков продаж, что даст ресурсы для инвестиций в здоровье и образование"
          </p>
        </div>
        
        <div className={styles.contentSection}>
          <h4 className={styles.contentHeader}>Трекинг стратегических изменений:</h4>
          <ul className={styles.contentList}>
              <li><strong>Метрики по сферам:</strong> Отслеживаем прогресс в каждой области.</li>
              <li><strong>Корреляционный эффект:</strong> Как развитие одной сферы влияет на другие.</li>
              <li><strong>Ресурсная эффективность:</strong> Где вы тратите силы с максимальной отдачей.</li>
              <li><strong>Стратегические корректировки:</strong> Адаптация плана на основе результатов.</li>
          </ul>
        </div>

        <div className={styles.contentSection}>
          <h4 className={styles.contentHeader}>Результат: Системный рост вместо точечных улучшений</h4>
          <p>
            Когда вы ставите цели с пониманием взаимосвязей между сферами, каждое достижение становится ступенькой к более высокому уровню жизни, а не просто галочкой в списке задач.
          </p>
        </div>
        
        <div className={styles.ctaSection}>
            <h3>Начните ставить стратегические цели уже сегодня</h3>
            <p>Превратите свои мечты в конкретные планы, которые высвободят ресурсы для развития всех сфер жизни.</p>
            <div className={styles.buttonRow}>
                <Link to="/signup" className={`${styles.btn} ${styles.btnPrimary}`}>Начать бесплатно</Link>
            </div>
        </div>
      </div>
    </>
  );
};

export default GoalsFeaturePage; 