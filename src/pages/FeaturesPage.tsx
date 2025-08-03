import React from 'react';
import { Helmet } from 'react-helmet-async';
import FeaturesIndexPage from './features/FeaturesIndexPage';

const FeaturesPage = () => {
  return (
    <>
      <Helmet>
        <title>Возможности HPI.expert — Платформа для вашего роста</title>
        <meta name="description" content="Откройте для себя все возможности платформы HPI.expert: от интерактивного дашборда и AI-рекомендаций до постановки целей и интеграции с другими сервисами." />
      </Helmet>
      <FeaturesIndexPage />
    </>
  );
};

export default FeaturesPage;