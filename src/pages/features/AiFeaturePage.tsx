import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import styles from '../Page.module.css';

const AiFeaturePage = () => {
  return (
    <>
      <Helmet>
        <title>AI-анализ корреляций между сферами жизни — HPI.expert</title>
        <meta name="description" content="Получите стратегический план развития от AI, который анализирует взаимосвязи между сферами жизни, выявляет дисбалансы и определяет приоритеты для максимального эффекта." />
      </Helmet>
      <div className={styles.page}>
        <h1>AI анализирует корреляции между сферами жизни</h1>
        <p className={styles.subheadline}>
          Получите стратегический план развития, основанный на понимании взаимосвязей, а не на общих советах
        </p>
        
        <h4>AI как стратегический аналитик</h4>
        <p>
          Наш искусственный интеллект — это не просто советчик, а стратегический аналитик вашего развития. Он анализирует корреляции между всеми сферами жизни и показывает, где именно нужно сфокусироваться для максимального эффекта.
        </p>

        <div className={styles.contentSection}>
          <h4 className={styles.contentHeader}>Что анализирует AI?</h4>
          <ul className={styles.contentList}>
            <li><strong>Корреляции между сферами:</strong> Как здоровье влияет на карьеру, а финансы на отношения.</li>
            <li><strong>Дисбалансы развития:</strong> Где у вас перекосы, которые блокируют рост.</li>
            <li><strong>Приоритеты действий:</strong> Что делать в первую очередь для прорыва.</li>
            <li><strong>Ресурсные ловушки:</strong> Где вы тратите силы без результата.</li>
            <li><strong>Скрытые возможности:</strong> Какие сферы могут дать неожиданный эффект.</li>
          </ul>
        </div>

        <div className={styles.contentSection}>
          <h4 className={styles.contentHeader}>Стратегические рекомендации вместо общих советов</h4>
          <p>
            Обычные коучи говорят: "Работайте над собой", "Ставьте цели", "Развивайте навыки".
            <br />
            AI HPI показывает: "Развитие здоровья на 20% даст прирост энергии на 40%, что позволит работать эффективнее и увеличить доход на 30%".
          </p>
        </div>
        
        <div className={styles.contentSection}>
          <h4 className={styles.contentHeader}>Как AI строит стратегию?</h4>
          <ul className={styles.contentList}>
            <li><strong>1. Анализ текущего состояния:</strong> Оценка всех 8 сфер жизни.</li>
            <li><strong>2. Выявление корреляций:</strong> Понимание взаимосвязей между сферами.</li>
            <li><strong>3. Расчет приоритетов:</strong> Что даст максимальный эффект при минимальных усилиях.</li>
            <li><strong>4. План действий:</strong> Конкретные шаги с измеримыми результатами.</li>
            <li><strong>5. Корректировка стратегии:</strong> Адаптация плана на основе ваших действий.</li>
          </ul>
        </div>

        <div className={styles.contentSection}>
          <h4 className={styles.contentHeader}>Результат: Стратегический план вместо хаотичных попыток</h4>
          <p>
            Вместо того чтобы пробовать разные подходы наугад, вы получаете четкий план, основанный на анализе ваших данных и понимании системных взаимосвязей.
          </p>
        </div>
        
        <div className={styles.ctaSection}>
            <h3>Получите свой стратегический план развития</h3>
            <p>Начните получать AI-рекомендации, основанные на анализе корреляций между сферами жизни.</p>
            <div className={styles.buttonRow}>
                <Link to="/signup" className={`${styles.btn} ${styles.btnPrimary}`}>Начать бесплатно</Link>
            </div>
        </div>
      </div>
    </>
  );
};

export default AiFeaturePage; 