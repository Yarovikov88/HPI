import React from 'react';
import { Helmet } from 'react-helmet-async';
import styles from './Page.module.css';

const MethodologyPage = () => {
  return (
    <>
      <Helmet>
        <title>Методология HPI — Научный подход к вашему развитию</title>
        <meta name="description" content="Узнайте, как лучшие мировые практики саморазвития и психологии были превращены в точную data-driven систему для вашего роста на платформе HPI.expert." />
      </Helmet>
      <div className={styles.page}>
        <h1>Методология HPI</h1>
        <p>Этот раздел находится в разработке.</p>
        <p>Здесь будет подробное описание нашей методологии, основанной на лучших мировых практиках...</p>
      </div>
    </>
  );
};

export default MethodologyPage;