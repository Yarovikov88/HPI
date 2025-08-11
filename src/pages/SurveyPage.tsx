import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useSurvey } from '../hooks/useSurvey';
import { SPHERES } from '../data/spheres';
// import CalendarWidget from '../components/CalendarWidget'; // Календарь не используется на этой странице
import styles from './SurveyPage.module.css';
import { toast } from 'sonner';

export default function SurveyPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const dateParam = searchParams.get('date');
  
  const { 
    groupedQuestions, 
    answers,
    updateAnswer, 
    loading,
    selectedDate,
    removeAnswer,
    // опционально присутствует в контексте
    saveSphereAnswers,
  } = useSurvey();

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

  // Вопросы текущей сферы
  const questionsInSphere = useMemo(() => (groupedQuestions[currentSphereId] || []) as any[], [groupedQuestions, currentSphereId]);

  // Индекс текущего вопроса в сфере (из URL ?q=)
  const currentQuestionIndex = useMemo(() => {
    const raw = searchParams.get('q');
    const idx = raw ? Number.parseInt(raw, 10) : 0;
    if (Number.isNaN(idx) || idx < 0) return 0;
    const max = Math.max(0, questionsInSphere.length - 1);
    return Math.min(idx, max);
  }, [searchParams, questionsInSphere.length]);

  const setQuestionIndex = (idx: number, sphereId = currentSphereId) => {
    const next: Record<string, string> = { sphere: sphereId, q: String(Math.max(0, idx)) };
    if (dateParam) next.date = dateParam;
    setSearchParams(next);
  };

  // Фолбэк-вопрос на случай пустых данных
  const buildFallbackQuestion = (sphereId: string) => ({
    id: `auto-${sphereId}`,
    text: `Оцените уровень удовлетворенности в сфере: ${SPHERES[sphereId]?.name || sphereId}`,
    options: ['Совсем нет', 'Скорее нет', 'Скорее да', 'Полностью да'],
    scores: [1, 2, 3, 4],
    sphere_id: sphereId,
    sphere_api_id: Math.max(1, Object.keys(SPHERES).indexOf(sphereId) + 1),
  } as any);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [currentSphereIndex]);

  useEffect(() => {
    if (!loading && sphereIds.length > 0) {
      const sphereFromParams = searchParams.get('sphere');
      if (!sphereFromParams || !sphereIds.includes(sphereFromParams)) {
        const next: Record<string, string> = { sphere: sphereIds[0], q: '0' };
        if (dateParam) next.date = dateParam;
        setSearchParams(next, { replace: true });
      } else {
        // Нормализуем q при смене сферы
        const qRaw = searchParams.get('q');
        if (!qRaw || Number(qRaw) > Math.max(0, questionsInSphere.length - 1)) {
          setQuestionIndex(0, sphereFromParams);
        }
      }
    }
  }, [loading, sphereIds, searchParams, setSearchParams, questionsInSphere.length, dateParam]);

  const handleAnswerChange = (questionId: string, value: number, sphereApiId: number | undefined) => {
    if (sphereApiId === undefined) {
      console.error("Не удалось определить ID сферы для вопроса:", questionId);
      return;
    }
    
    const currentAnswer = answers[questionId];
    const isDeselecting = currentAnswer?.answer === value;

    if (isDeselecting) {
      // Снятие выбора: удаляем ответ (локально и на сервере, если есть id)
      removeAnswer(questionId);
    } else {
      // Логика для выбора или изменения ответа
      updateAnswer({
        question_id: questionId as any,
        answer: value,
        sphere: Number(sphereApiId) as any,
      });
    }
  };
  
  const validateCurrentQuestion = () => {
    const q = questionsInSphere[currentQuestionIndex];
    if (!q) return true;
    // Разрешаем просмотр без ответа, если выбранная дата не сегодня
    const params = new URLSearchParams(window.location.search);
    const dateParam = params.get('date');
    const todayStr = new Date().toISOString().split('T')[0];
    const isToday = !dateParam || dateParam === todayStr;
    if (!isToday) return true;
    if (!answers[q.id]) {
      toast.error('Пожалуйста, ответьте на вопрос, прежде чем продолжить.');
      return false;
    }
    return true;
  };

  const handlePrev = () => {
    if (currentQuestionIndex > 0) {
      setQuestionIndex(currentQuestionIndex - 1);
      return;
    }
    // Переход к предыдущей сфере на последний её вопрос
    const prevSphereIdx = currentSphereIndex - 1;
    if (prevSphereIdx >= 0) {
      const prevSphereId = sphereIds[prevSphereIdx];
      const prevLen = (groupedQuestions[prevSphereId] || []).length;
      const next: Record<string, string> = { sphere: prevSphereId, q: String(Math.max(0, prevLen - 1)) };
      if (dateParam) next.date = dateParam;
      setSearchParams(next);
    }
  };

  const handleNext = async () => {
    if (!validateCurrentQuestion()) return;
    const lastIdxInSphere = Math.max(0, questionsInSphere.length - 1);
    if (currentQuestionIndex < lastIdxInSphere) {
      setQuestionIndex(currentQuestionIndex + 1);
      return;
    }
    // Последний вопрос сферы — сохраняем и переходим к следующей сфере
    if (typeof saveSphereAnswers === 'function') {
      await saveSphereAnswers(currentSphereId);
    }
    const nextSphereIdx = currentSphereIndex + 1;
    if (nextSphereIdx < sphereIds.length) {
      const nextSphereId = sphereIds[nextSphereIdx];
      const params = new URLSearchParams(window.location.search);
      const dateParam = params.get('date');
      const next: Record<string, string> = { sphere: nextSphereId, q: '0' };
      if (dateParam) next.date = dateParam;
      setSearchParams(next);
    }
  };
  
  const handleFinish = async () => {
    if (!validateCurrentQuestion()) return;
    if (typeof saveSphereAnswers === 'function') {
      await saveSphereAnswers(currentSphereId);
    }
    navigate('/account/diagnostics', { replace: true });
  };

  if (loading) return <div>Загрузка...</div>;

  if (sphereIds.length === 0) {
    return <div>Не удалось загрузить вопросы для базовой диагностики. Возможно, они еще не созданы для вашего аккаунта.</div>
  }
  
  if (!currentSphereId) {
    return <div>Инициализация...</div>;
  }

  const sphereData = SPHERES[currentSphereId];
  const sphereIcon = sphereData ? sphereData.emoji : '';
  const sphereText = sphereData ? sphereData.name : currentSphereId;

  const isLastSphere = currentSphereIndex === sphereIds.length - 1;
  const isLastQuestionInSphere = currentQuestionIndex === Math.max(0, questionsInSphere.length - 1);

  return (
    <div>
      <div className={styles.header}>
        <h1 className={styles.pageTitle}>
          <span className={styles.titleIcon}>{sphereIcon}</span>
          {sphereText} ({currentSphereIndex + 1}/{sphereIds.length})
        </h1>
        <div className={styles.dateBadge}>
          {selectedDate.toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric' })}
        </div>
      </div>
      
      <form onSubmit={(e) => e.preventDefault()}>
        {(() => {
          const q = questionsInSphere[currentQuestionIndex] || buildFallbackQuestion(currentSphereId);
          const currentAnswer = answers[q.id];
          const displayText = q.text && q.text.trim().length > 0
            ? q.text
            : `Оцените уровень удовлетворенности в сфере: ${SPHERES[q.sphere_id]?.name || q.sphere_id}`;
          const options: string[] = Array.isArray(q.options) && q.options.length > 0
            ? q.options
            : ['Совсем нет', 'Скорее нет', 'Скорее да', 'Полностью да'];

          return (
            <div key={q.id} className={styles.questionContainer}>
              <p className={styles.questionText}>{displayText}</p>
              <div className={styles.optionsContainer}>
                {options.map((choice: string, index: number) => {
                  const scores: number[] | undefined = Array.isArray(q.scores) && q.scores.length === options.length ? q.scores : undefined;
                  const answerValue = scores ? scores[index] : index + 1;
                  const isSelected = String(currentAnswer?.answer) === String(answerValue);
                  return (
                    <button
                      key={`${q.id}-${choice}`}
                      type="button"
                      onClick={() => handleAnswerChange(q.id, answerValue, q.sphere_api_id ?? Math.max(1, Object.keys(SPHERES).indexOf(q.sphere_id) + 1))}
                      className={`${styles.optionButton} ${isSelected ? styles.selected : ''}`}
                      disabled={false}
                    >
                      {choice}
                    </button>
                  );
                })}
              </div>
              <div className={styles.progressInfo}>
                Вопрос {Math.min(currentQuestionIndex + 1, Math.max(1, questionsInSphere.length))}/{Math.max(1, questionsInSphere.length)}
              </div>
            </div>
          );
        })()}
      </form>

      <div className={styles.navigationButtons}>
        <button
          type="button"
          onClick={handlePrev}
          disabled={currentSphereIndex === 0 && currentQuestionIndex === 0}
          className={styles.navigationButton}
        >
          Назад
        </button>
        <button
          type="button"
          onClick={handleNext}
          disabled={false}
          className={styles.navigationButton}
        >
          Вперед
        </button>
        <button
          type="button"
          onClick={handleFinish}
          className={styles.finishButton}
        >
          Завершить
        </button>
      </div>
    </div>
  );
}