import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import HeroBanner from './HeroBanner';
import styles from './Home.module.css';
import { sections } from './sections';

export default function Home() {
  return (
    <>
      <Helmet>
        <title>HPI.EXPERT — управление развитием</title>
        <meta name="description" content="Платформа для оценки и развития вашего потенциала. Отслеживайте прогресс в ключевых сферах жизни, получайте персональные AI-рекомендации и стройте системный путь к успеху." />
      </Helmet>
      <div className={styles.heroContainer}>
        <HeroBanner />
      </div>
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
    </>
  );
} 