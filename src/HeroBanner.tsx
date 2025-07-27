import React from 'react';
import authorPhoto from './assets/author.jpg'; // Ваше фото
import styles from './HeroBanner.module.css';
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
                        <Link to="/login" className={styles.primaryBtn}>
                            Попробовать бесплатно
                        </Link>
                        <a href="/how-it-works" className={styles.secondaryBtn}>
                            Как это работает?
                        </a>
                    </div>
                </div>
                <div className={styles.profileContainer}>
                    <img
                        src={authorPhoto} // Используем ваше фото
                        alt="Андрей Яровиков"
                        className={styles.profilePhoto}
                    />
                    <p className={styles.profileCaption}>
                        <b>Андрей Яровиков</b>
                        <br />
                        основатель HPI.expert
                    </p>
                </div>
            </div>
        </div>
    );
};

export default HeroBanner; 