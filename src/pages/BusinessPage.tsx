import React from 'react';
import { Helmet } from 'react-helmet-async';
import styles from './Page.module.css';

const BusinessPage = () => {
  return (
    <>
      <Helmet>
        <title>HPI для бизнеса — Развивайте команды</title>
        <meta name="description" content="Узнайте, как HPI.expert помогает повышать вовлеченность и развивать потенциал сотрудников. Платформа для системного роста вашей команды." />
      </Helmet>
      <div className={styles.page}>
        <h1>Для бизнеса</h1>
        <p>Этот раздел находится в разработке.</p>
        <p>Здесь будет информация о решениях для корпоративных клиентов.</p>
      </div>
    </>
  );
};

export default BusinessPage;