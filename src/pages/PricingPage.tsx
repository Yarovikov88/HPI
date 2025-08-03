import React from 'react';
import { Helmet } from 'react-helmet-async';
import styles from './Page.module.css';
import buttonStyles from '../components/Button.module.css';
import { Link } from 'react-router-dom';

const PricingPage = () => {
  return (
    <>
      <Helmet>
        <title>Тарифы — HPI.expert</title>
        <meta name="description" content="Выберите подходящий тарифный план HPI.expert. Начните бесплатно или получите доступ ко всем Pro-возможностям для максимального роста." />
      </Helmet>
      <div className={styles.page}>
        <div className={styles.pricingHeader}>
            <h1>Выберите свой тариф</h1>
            <p>Начните бесплатно и переходите на Pro, когда будете готовы к максимальным результатам.</p>
        </div>

        <div className={styles.pricingGrid}>
            <div className={styles.pricingCard}>
                <div className={styles.cardContent}>
                    <h2>Базовый</h2>
                    <p>Для личного пользования</p>
                    <ul>
                        <li>Доступ к базовой диагностике</li>
                        <li>Личный кабинет</li>
                        <li>История ответов</li>
                    </ul>
                </div>
                <button className={buttonStyles.ctaButton}>Начать бесплатно</button>
            </div>

            <div className={`${styles.pricingCard} ${styles.pricingCardFeatured}`}>
                <div className={styles.cardContent}>
                    <h2>PRO</h2>
                    <p>Для профессионального развития</p>
                    <ul>
                        <li>Все из базового</li>
                        <li>Расширенная диагностика</li>
                        <li>AI-рекомендации</li>
                        <li>Доступ к PRO-отчетам</li>
                        <li>Поддержка эксперта</li>
                    </ul>
                </div>
                <button className={buttonStyles.ctaButton}>Попробовать PRO</button>
            </div>

            <div className={styles.pricingCard}>
                <div className={styles.cardContent}>
                    <h2>Для бизнеса</h2>
                    <p>Для команд и организаций</p>
                    <ul>
                        <li>Все из PRO</li>
                        <li>Командная аналитика</li>
                        <li>Интеграции</li>
                        <li>Персонализированные решения</li>
                    </ul>
                </div>
                <button className={buttonStyles.ctaButton}>Запросить демо</button>
            </div>
        </div>
      </div>
    </>
  );
};

export default PricingPage; 