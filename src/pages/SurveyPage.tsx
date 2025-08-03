import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
// import { apiClient, type AnswerPayload } from '../services/api';
import { useSurvey } from '../hooks/useSurvey';
import { SPHERES } from '../data/spheres';
import styles from './SurveyPage.module.css';
// Я предполагаю, что компонент вопроса называется Question, и импортирую его
// УДАЛЯЕМ СЛОМАННЫЙ ИМПОРТ
// import Question from '../components/Question'; 
import { toast } from 'sonner';

export default function SurveyPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Получаем всё необходимое из контекста
  const { 
    groupedQuestions, 
    answers, // Получаем актуальные ответы
    updateAnswer, 
    removeAnswer,
    isSphereComplete,
    isBasicSurveyComplete,
    loading 
  } = useSurvey();

  const [submitting, setSubmitting] = useState(false);
  const [currentQuestions, setCurrentQuestions] = useState<any[]>([]);
  
  const sphereIds = useMemo(() => {
      const sphereOrder = Object.keys(SPHERES);
      return Object.keys(groupedQuestions).sort((a, b) => sphereOrder.indexOf(a) - sphereOrder.indexOf(b));
  }, [groupedQuestions]);

  const currentSphereId = useMemo(() => {
    const sphere = searchParams.get('sphere');
    if (sphere && sphereIds.includes(sphere)) {
      return sphere;
    }
    return sphereIds[0] || '';
  }, [searchParams, sphereIds]);
  
  const currentSphereIndex = useMemo(() => Math.max(0, sphereIds.indexOf(currentSphereId)), [sphereIds, currentSphereId]);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [currentSphereIndex]);

  useEffect(() => {
    // Устанавливаем правильный sphereId в URL, если он некорректен или отсутствует
    if (!loading && sphereIds.length > 0) {
      const sphereFromParams = searchParams.get('sphere');
      if (!sphereFromParams || !sphereIds.includes(sphereFromParams)) {
        setSearchParams({ sphere: sphereIds[0] }, { replace: true });
      }
    }
  }, [loading, sphereIds, searchParams, setSearchParams]);

  /*
  useEffect(() => {
    // Проверка, чтобы убедиться, что мы не перепрыгнули через незаполненный шаг
    if (loading || !currentSphereId) return;

    const targetIndex = sphereIds.indexOf(currentSphereId);

    for (let i = 0; i < targetIndex; i++) {
      if (!isSphereComplete(sphereIds[i])) {
        setValidationError('Пожалуйста, сначала заполните предыдущие разделы.');
        setSearchParams({ sphere: sphereIds[i] }, { replace: true });
        return;
      }
    }
  }, [currentSphereId, sphereIds, isSphereComplete, loading, setSearchParams]);
  */
  
  useEffect(() => {
    if (currentSphereId && groupedQuestions[currentSphereId]) {
      setCurrentQuestions(groupedQuestions[currentSphereId]);
    }
  }, [currentSphereId, groupedQuestions]);

  const handleAnswerChange = (questionId: string, value: number) => {
    const isDeselecting = answers[questionId] === value;

    if (isDeselecting) {
      // Логика для снятия выбора пока не реализована на бэкенде,
      // поэтому просто удаляем локально
      removeAnswer(questionId);
      // apiClient.deleteAnswer(questionId); // УДАЛЯЕМ ВЫЗОВ
    } else {
      updateAnswer(questionId, value);
      // Этот вызов будет либо создавать новый ответ, либо обновлять существующий
      // (если на бэкенде реализована логика upsert)
      // apiClient.submitAnswer({ question_id: questionId, answer: value });
    }
  };
  
  const validateCurrentSphere = () => {
    const questionsOnPage = groupedQuestions[currentSphereId] || [];
    for (const q of questionsOnPage) {
      if (answers[q.id] === undefined) {
        toast.error('Пожалуйста, ответьте на все вопросы, прежде чем продолжить.');
        return false;
      }
    }
    return true;
  };

  const handleNavigation = (newIndex: number) => {
    if (newIndex > currentSphereIndex && !validateCurrentSphere()) {
      return;
    }
    if (newIndex >= 0 && newIndex < sphereIds.length) {
      setSearchParams({ sphere: sphereIds[newIndex] });
    }
  };
  
  const handleFinish = () => {
    if (!validateCurrentSphere()) {
      return;
    }
    navigate('/account/diagnostics', { replace: true });
  };

  if (loading) return <div>Загрузка...</div>;

  // Если после загрузки вопросы не появились, сообщаем об этом
  if (sphereIds.length === 0) {
    return <div>Не удалось загрузить вопросы для базовой диагностики. Возможно, они еще не созданы для вашего аккаунта.</div>
  }
  
  // Этот код останется на случай, если sphereId еще не установлен в URL
  if (!currentSphereId) {
    return <div>Инициализация...</div>;
  }

  const sphereData = SPHERES[currentSphereId];
  const sphereIcon = sphereData ? sphereData.emoji : '';
  const sphereText = sphereData ? sphereData.name : currentSphereId;

  const isLastSphere = currentSphereIndex === sphereIds.length - 1;

  return (
    <div>
      <h1 className={styles.pageTitle}>
        <span className={styles.titleIcon}>{sphereIcon}</span>
        {sphereText} ({currentSphereIndex + 1}/{sphereIds.length})
      </h1>
      
      <form onSubmit={(e) => e.preventDefault()}>
        {currentQuestions.map(q => (
          <div key={q.id} className={styles.questionContainer}>
            <p className={styles.questionText}>{q.text}</p>
            <div className={styles.optionsContainer}>
              {q.options?.map((choice: string, index: number) => {
                // Ищем соответствующий score. Если его нет, используем сам choice (для обратной совместимости)
                const answerValue = q.scores ? q.scores[index] : index;
                const isSelected = answers[q.id] === answerValue;
                
                return (
                  <button
                    key={`${q.id}-${choice}`}
                    type="button"
                    onClick={() => handleAnswerChange(q.id, answerValue)}
                    className={`${styles.optionButton} ${isSelected ? styles.selected : ''}`}
                  >
                    {choice}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
        <div className={styles.navigationButtons}>
          <button type="button" onClick={() => handleNavigation(currentSphereIndex - 1)} disabled={currentSphereIndex === 0}>Назад</button>
          {isLastSphere ? (
             <button type="button" onClick={handleFinish} disabled={submitting}>{submitting ? 'Сохранение...' : 'Завершить'}</button>
          ) : (
             <button type="button" onClick={() => handleNavigation(currentSphereIndex + 1)} disabled={submitting}>Далее</button>
          )}
        </div>
      </form>
    </div>
  );
} 