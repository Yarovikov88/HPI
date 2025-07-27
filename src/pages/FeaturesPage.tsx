import React from 'react';
import { Helmet } from 'react-helmet-async';
import styles from './Page.module.css';

const FeaturesPage = () => {
  return (
    <>
      <Helmet>
        <title>Возможности HPI.expert — Платформа для вашего роста</title>
        <meta name="description" content="Откройте для себя все возможности платформы HPI.expert: от интерактивного дашборда и AI-рекомендаций до постановки целей и интеграции с другими сервисами." />
      </Helmet>
      <div className={styles.page}>
        <h1>Возможности платформы</h1>
        <p>Этот раздел находится в разработке.</p>
        <p>Здесь будет подробное описание всех ключевых возможностей: дашборды, AI-рекомендации, трекинг целей и многое другое.</p>
      </div>
    </>
  );
};

export default FeaturesPage;