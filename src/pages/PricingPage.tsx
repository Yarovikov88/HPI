import React from 'react';
import { Helmet } from 'react-helmet-async';
import styles from './Page.module.css';

const PricingPage = () => {
  return (
    <>
      <Helmet>
        <title>Тарифы — HPI.expert</title>
        <meta name="description" content="Выберите подходящий тарифный план HPI.expert. Начните бесплатно или получите доступ ко всем Pro-возможностям для максимального роста." />
      </Helmet>
      <div className={styles.page}>
        <h1>Тарифы</h1>
        <p>Этот раздел находится в разработке.</p>
        <p>Здесь будет информация о наших тарифных планах.</p>
      </div>
    </>
  );
};

export default PricingPage; 