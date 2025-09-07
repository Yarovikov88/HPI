import React from 'react';
import logoHPI from './assets/logo HPI.jpg'; // Новый логотип
import styles from './HeroBanner.module.css';
import buttonStyles from './components/Button.module.css'; // Исправляем путь
import { Link } from 'react-router-dom'; // Возвращаем Link

const HeroBanner = () => {
    return (
        <div className={styles.heroContainer}>
            <div className={styles.heroBanner}>
                <div className={styles.heroContent}>
                    <h1 className={styles.heroTitle}>
                        Управляйте развитием на основе данных, а не догадок
                    </h1>
                    <p className={styles.heroSubtitle}>
                        HPI.EXPERT — это платформа для оценки и развития вашего
                        потенциала. Отслеживайте прогресс в ключевых сферах жизни,
                        получайте персональные AI-рекомендации и стройте системный путь к
                        успеху.
                    </p>
                    <div className={styles.ctaContainer}>
                        <Link to="/login" className={buttonStyles.ctaButton}>
                            Попробовать бесплатно
                        </Link>
                        <Link to="/methodology" className={buttonStyles.secondaryButton}>
                            Как это работает?
                        </Link>
                    </div>
                </div>
                <div className={styles.profileContainer}>
                    <img
                        src={logoHPI}
                        alt="HPI.expert logo"
                        className={styles.profilePhoto}
                    />
                </div>
            </div>
        </div>
    );
};

export default HeroBanner; 