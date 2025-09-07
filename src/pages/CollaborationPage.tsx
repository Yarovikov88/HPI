import React from 'react';
import { Helmet } from 'react-helmet-async';
import styles from './Page.module.css';

const CollaborationPage = () => {
  return (
    <>
      <Helmet>
        <title>Сотрудничество — HPI.EXPERT</title>
        <meta name="description" content="Варианты сотрудничества: от персонального консалтинга до реализации IT-проектов." />
      </Helmet>
      <div className={styles.pageContainer}>
        <header className={styles.pageHeader}>
          <h1>Сотрудничество</h1>
          <p className={styles.pageSubtitle}>Возможности для совместной работы: от индивидуальных консультаций и стратегических сессий до партнерства и разработки IT-решений.</p>
        </header>
        
        <main className={styles.mainContent}>
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Для частных лиц</h2>
            <div className={styles.cardsGrid}>
              <div className={styles.card}>
                <h3>Индивидуальные консультации</h3>
                <p>Глубокий анализ вашей текущей ситуации, определение ключевых точек роста и разработка персональной дорожной карты развития.</p>
              </div>
              <div className={styles.card}>
                <h3>Наставничество (менторинг)</h3>
                <p>Долгосрочное сопровождение на пути к вашим целям, регулярные сессии для коррекции курса, мотивации и решения сложных задач.</p>
              </div>
            </div>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Для бизнеса и команд</h2>
            <div className={styles.cardsGrid}>
              <div className={styles.card}>
                <h3>Стратегические сессии для команд</h3>
                <p>Фасилитация командной работы для определения векторов развития, решения комплексных проблем и повышения общей эффективности.</p>
              </div>
              <div className={styles.card}>
                <h3>Экспертиза и аудит IT-проектов</h3>
                <p>Независимая оценка текущих проектов, выявление узких мест и разработка рекомендаций по оптимизации процессов и архитектуры.</p>
              </div>
              <div className={styles.card}>
                <h3>Разработка IT-систем под ключ</h3>
                <p>Вместе с моей командой мы готовы взять на себя полный цикл разработки специализированных IT-решений для вашего бизнеса.</p>
              </div>
            </div>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Партнерство для экспертов</h2>
            <div className={styles.centeredContent}>
              <p>Я всегда открыт к сотрудничеству с коучами, психологами, тренерами и другими экспертами в области человеческого развития. Если вы разделяете мои ценности и системный подход, мы можем создавать совместные продукты, проводить мероприятия или интегрировать ваши методики в HPI.expert.</p>
              <a href="mailto:expert@hpi.expert" className={styles.ctaButton}>Связаться</a>
            </div>
          </section>
        </main>
      </div>
    </>
  );
};

export default CollaborationPage; 