import React from 'react';
import { Helmet } from 'react-helmet-async';
import styles from '../Page.module.css';

const DashboardFeaturePage = () => {
  return (
    <>
      <Helmet>
        <title>Интерактивный дашборд — HPI.expert</title>
        <meta name="description" content="Вся аналитика по вашему развитию в одном месте. Отслеживайте HPI, ключевые метрики и прогресс по целям с помощью интерактивного дашборда." />
      </Helmet>
      <div className={styles.page}>
        <h1>Интерактивный дашборд</h1>
        <p>Этот раздел находится в разработке.</p>
      </div>
    </>
  );
};

export default DashboardFeaturePage; 