import React, { useMemo, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSurvey } from '../hooks/useSurvey';
import ProQuestionForm from '../components/ProQuestionForm';
import { SPHERES } from '../data/spheres';
import styles from './ProSurveyPage.module.css';

const proCategories = ['problems', 'goals', 'blockers', 'metrics', 'achievements']; 

const categoryTranslations: { [key: string]: string } = {
  problems: "Проблемы",
  goals: "Цели",
  blockers: "Блокеры",
  metrics: "Метрики",
  achievements: "Достижения",
};

export default function ProSurveyPage() {
  const navigate = useNavigate();
  const { category = proCategories[0] } = useParams<{ category: string }>();

  const {
    groupedProQuestions,
    proAnswers,
    updateProAnswer,
    loading,
  } = useSurvey();

  const currentCategoryIndex = useMemo(() => {
    const index = proCategories.indexOf(category);
    return index === -1 ? 0 : index;
  }, [category]);

  const questionsForCategory = useMemo(() => {
    return groupedProQuestions[category] || [];
  }, [category, groupedProQuestions]);

  // Redirect to the first category if the URL is invalid
  useEffect(() => {
    if (!proCategories.includes(category)) {
      navigate(`/account/pro/${proCategories[0]}`, { replace: true });
    }
  }, [category, navigate]);

  const handleNavigation = (direction: 'next' | 'prev') => {
    const newIndex = direction === 'next' ? currentCategoryIndex + 1 : currentCategoryIndex - 1;
    if (newIndex >= 0 && newIndex < proCategories.length) {
      navigate(`/account/pro/${proCategories[newIndex]}`);
    } else if (direction === 'next') {
      // Finished the survey
      navigate('/account/pro-dashboard');
    }
  };

  if (loading) {
    return <div>Загрузка Pro-опроса...</div>;
  }
  
  if (!questionsForCategory.length) {
      return <div>Для категории "{categoryTranslations[category] || category}" не найдено вопросов.</div>
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.pageTitle}>Pro-опрос: {categoryTranslations[category] || category}</h1>
      <div className={styles.formsContainer}>
        {questionsForCategory.map(question => {
          const sphereInfo = SPHERES[question.sphere_id] || { id: 'unknown', name: 'Unknown Sphere', emoji: '❓' };
          return (
            <ProQuestionForm
              key={question.id}
              sphere={sphereInfo}
              questionId={question.id}
              answer={proAnswers[question.id] || ''}
              onAnswerChange={updateProAnswer}
            />
          );
        })}
      </div>

      <div className={styles.navigationButtons}>
        <button onClick={() => handleNavigation('prev')} disabled={currentCategoryIndex === 0}>
          Назад
        </button>
        <button onClick={() => handleNavigation('next')}>
          {currentCategoryIndex === proCategories.length - 1 ? 'Завершить' : 'Далее'}
        </button>
      </div>
    </div>
  );
}