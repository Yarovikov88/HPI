import React from 'react';
import { Helmet } from 'react-helmet-async';
import styles from '../Page.module.css';

const AiFeaturePage = () => {
  return (
    <>
      <Helmet>
        <title>Персональные AI-рекомендации — HPI.expert</title>
        <meta name="description" content="Получайте советы от искусственного интеллекта, основанные на ваших данных, для принятия эффективных решений и ускорения вашего роста." />
      </Helmet>
      <div className={styles.page}>
        <h1>Персональные AI-рекомендации</h1>
        <p>Этот раздел находится в разработке.</p>
      </div>
    </>
  );
};

export default AiFeaturePage; 