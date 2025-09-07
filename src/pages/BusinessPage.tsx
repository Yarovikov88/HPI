import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import styles from './Page.module.css';

const BusinessPage = () => {
  return (
    <>
      <Helmet>
        <title>HPI для Бизнеса — Стратегическое развитие бизнеса</title>
        <meta name="description" content="Примените стратегический подход HPI для командного роста. Решения для бизнеса, коучей, психологов и HR-агентств." />
      </Helmet>
      <div className={styles.page}>
        <h1>HPI для Бизнеса</h1>
        <p className={styles.subheadline}>
          Примените стратегический подход к развитию не только для личного, но и для командного роста
        </p>

        <div className={styles.contentSection}>
          <h4 className={styles.contentHeader}>Для команд: Системное развитие потенциала</h4>
          <p>
            HPI.EXPERT помогает руководителям выявлять и развивать потенциал сотрудников через понимание взаимосвязей между различными аспектами их развития.
          </p>
        </div>
        
        <div className={styles.contentSection}>
          <h4 className={styles.contentHeader}>Возможности для бизнеса:</h4>
          <ul className={styles.contentList}>
            <li><strong>Стратегический анализ команды:</strong> Выявление дисбалансов в развитии коллектива.</li>
            <li><strong>Корреляционный дашборд:</strong> Понимание, как развитие одной области влияет на другие.</li>
            <li><strong>Приоритизация развития:</strong> Определение, какие навыки развивать в первую очередь.</li>
            <li><strong>Ресурсное планирование:</strong> Эффективное распределение времени и бюджета на развитие.</li>
            <li><strong>Измеримые результаты:</strong> Конкретные метрики роста потенциала команды.</li>
          </ul>
        </div>
        
        <div className={styles.contentSection}>
          <h4 className={styles.contentHeader}>Для партнеров: Интеграция HPI в ваши услуги</h4>
          <p>
            Коучи, психологи, менторы и HR-агентства могут использовать HPI.EXPERT как мощный инструмент для работы с клиентами.
          </p>
        </div>

        <div className={styles.contentSection}>
          <h4 className={styles.contentHeader}>Что получают партнеры:</h4>
          <ul className={styles.contentList}>
              <li><strong>Инструмент стратегического анализа:</strong> Вместо общих советов — конкретные данные.</li>
              <li><strong>Дополнительный источник дохода:</strong> Монетизация через HPI-консультации.</li>
              <li><strong>Дифференциация от конкурентов:</strong> Уникальный подход к развитию клиентов.</li>
              <li><strong>Измеримые результаты:</strong> Конкретные метрики эффективности вашей работы.</li>
              <li><strong>Масштабируемость:</strong> Работа с большим количеством клиентов одновременно.</li>
          </ul>
        </div>
        
        <div className={styles.ctaSection}>
          <h4>Готовы развивать потенциал своей команды?</h4>
          <p>Получите персональное предложение для вашей компании и начните строить культуру стратегического развития уже сегодня.</p>
          <div className={styles.buttonRow}>
            <Link to="/signup" className={`${styles.btn} ${styles.btnPrimary}`}>Начать бесплатно</Link>
          </div>
        </div>

      </div>
    </>
  );
};

export default BusinessPage;