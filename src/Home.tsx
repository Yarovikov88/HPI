import React from 'react';
import { Helmet } from 'react-helmet-async';
import HeroBanner from './HeroBanner';
import styles from './Home.module.css';
import { Link } from 'react-router-dom';
import { sections } from './sections';

const Home = () => {
  return (
    <>
      <Helmet>
        <title>HPI.expert — Платформа для управления личным развитием</title>
        <meta name="description" content="HPI.expert — это data-driven платформа для оценки и развития вашего потенциала. Отслеживайте прогресс, получайте AI-рекомендации и стройте системный путь к успеху." />
      </Helmet>
      <div className={styles.heroContainer}>
        <HeroBanner />
      </div>
      <main className={styles.mainContent}>
        <div className={styles.container}>
          <div className={styles.sectionsGrid}>
            {sections.filter(section => section.link).map(section => {
              const isExternal = section.link!.startsWith('http');

              const cardContent = (
                <>
                  <h2 className={styles.sectionTitle}>{section.title}</h2>
                  <p className={styles.sectionDesc}>{section.description}</p>
                </>
              );

              if (isExternal) {
                return (
                  <a href={section.link} key={section.title} target="_blank" rel="noopener noreferrer" className={styles.sectionCard}>
                    {cardContent}
                  </a>
                );
              }
              
              return (
                <Link to={section.link!} key={section.title} className={styles.sectionCard}>
                  {cardContent}
                </Link>
              );
            })}
          </div>
        </div>
      </main>
    </>
  );
}

export default Home; 