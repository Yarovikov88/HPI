import React from 'react';
import { Helmet } from 'react-helmet-async';
import HeroBanner from './HeroBanner';
import styles from './Home.module.css';
import { Link } from 'react-router-dom';
import { sections } from './sections';

const Home = () => {
  // Все 6 блоков в одном массиве
  const allSections = sections;

  return (
    <>
      <Helmet>
        <title>HPI.EXPERT — Платформа для управления личным развитием</title>
        <meta name="description" content="HPI.EXPERT — это data-driven платформа для оценки и развития вашего человеческого потенциала. Отслеживайте прогресс, получайте AI-рекомендации и стройте системный путь к успеху." />
      </Helmet>
      <HeroBanner />
      <main className={styles.mainContent}>
        <div className={styles.container}>
          <section className={styles.section}>
            <h2 className={styles.sectionHeading}>Возможности платформы</h2>
            <div className={styles.featuresGrid}>
              {allSections.map(section => (
                section.link ? (
                  <Link to={section.link} key={section.id} className={styles.featureCard}>
                    <h3>{section.title}</h3>
                    <p>{section.description}</p>
                  </Link>
                ) : (
                  <div key={section.id} className={styles.featureCard}>
                    <h3>{section.title}</h3>
                    <p>{section.description}</p>
                  </div>
                )
              ))}
            </div>
          </section>
        </div>
      </main>
    </>
  );
}

export default Home; 