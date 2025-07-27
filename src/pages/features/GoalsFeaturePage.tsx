import React from 'react';
import { Helmet } from 'react-helmet-async';
import styles from '../Page.module.css';

const GoalsFeaturePage = () => {
  return (
    <>
      <Helmet>
        <title>Цели и трекинг — HPI.expert</title>
        <meta name="description" content="Ставьте амбициозные цели, разбивайте их на шаги и отслеживайте достижение в реальном времени. Системный подход к реализации ваших планов." />
      </Helmet>
      <div className={styles.page}>
        <h1>Цели и трекинг</h1>
        <p>Этот раздел находится в разработке.</p>
      </div>
    </>
  );
};

export default GoalsFeaturePage; 