import React, { useMemo, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useSurvey } from '../hooks/useSurvey';
import ProQuestionForm from '../components/ProQuestionForm';
// import CalendarWidget from '../components/CalendarWidget'; // УДАЛЯЕМ ЭТОТ ИМПОРТ
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
  const location = useLocation();
  const { category = proCategories[0] } = useParams<{ category: string }>();

  const {
    groupedProQuestions,
    proAnswers,
    updateProAnswerLocal,
    // добавим метод пакетного сохранения
    saveProCategoryAnswers,
    loading,
    selectedDate,     // Получаем дату
    // setSelectedDate,  // Получаем функцию для изменения даты
    setSelectedDate,
  } = useSurvey();

  const searchParams = new URLSearchParams(location.search);
  const dateParam = searchParams.get('date');
  // Сравниваем с ЛОКАЛЬНОЙ датой, а не UTC, чтобы не было ложной блокировки по часовому поясу
  const getLocalYMD = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  const todayStr = getLocalYMD(new Date());
  const isToday = !dateParam || dateParam === todayStr;

  useEffect(() => {
    if (dateParam) {
      const d = new Date(dateParam);
      if (!Number.isNaN(d.getTime())) setSelectedDate(d);
    }
  }, [dateParam, setSelectedDate]);

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
    const doNavigate = async () => {
      if (direction === 'next' && saveProCategoryAnswers) {
        await saveProCategoryAnswers(category);
      }
      const newIndex = direction === 'next' ? currentCategoryIndex + 1 : currentCategoryIndex - 1;
      if (newIndex >= 0 && newIndex < proCategories.length) {
        navigate(`/account/pro/${proCategories[newIndex]}${dateParam ? `?date=${dateParam}` : ''}`);
      } else if (direction === 'next') {
        navigate(`/account/pro-dashboard${dateParam ? `?date=${dateParam}` : ''}`);
      }
    };
    // запустить асинхронно
    void doNavigate();
  };

  if (loading) {
    return <div>Загрузка Pro-опроса...</div>;
  }
  
  if (!questionsForCategory.length) {
      return <div>Для категории "{categoryTranslations[category] || category}" не найдено вопросов.</div>
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.pageTitle}>Pro-опрос: {categoryTranslations[category] || category}</h1>
        {/* Добавляем бейдж с датой */}
        <div className={styles.dateBadge}>
          {selectedDate.toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric' })}
        </div>
      </div>
      
      <div className={styles.formsContainer}>
        {questionsForCategory.map(question => {
          const sphereInfo = SPHERES[question.sphere_id] || { id: 'unknown', name: 'Unknown Sphere', emoji: '❓' };
          
          // Обновленная логика получения ответа
          const proAnswerKey = `${category}-${question.sphere_id}`;
          const numericKey = `${category}-${String(question.sphere_api_id ?? Math.max(1, Object.keys(SPHERES).indexOf(question.sphere_id) + 1))}`;
          const currentAnswer = proAnswers[proAnswerKey]?.text || proAnswers[numericKey]?.text || '';

          return (
            <ProQuestionForm
              key={`${category}-${question.sphere_id}`}
              sphere={sphereInfo}
              answer={currentAnswer}
              onAnswerChange={(newAnswer) => {
                const sphereApiId = (question.sphere_api_id ?? Math.max(1, Object.keys(SPHERES).indexOf(question.sphere_id) + 1)) as number;
                // Локально обновляем, а сохранение уедет пакетно по кнопке "Далее"
                updateProAnswerLocal?.({ sphere: sphereApiId, text: newAnswer }, category);
              }}
              readOnly={false}
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