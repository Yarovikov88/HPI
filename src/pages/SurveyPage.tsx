import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useSurvey } from '../hooks/useSurvey';
import { SPHERES } from '../data/spheres';
// import CalendarWidget from '../components/CalendarWidget'; // Календарь не используется на этой странице
import styles from './SurveyPage.module.css';
import { toast } from 'sonner';
import { useSwipe } from '../hooks/useSwipe';
import { ProBasicHeader } from '../components/ProBasicHeader';

const parseYmd = (ymd: string): Date | null => {
  const parts = ymd.split('-');
  if (parts.length !== 3) return null;
  const year = parseInt(parts[0], 10);
  const month = parseInt(parts[1], 10) - 1; // Month is 0-indexed in JS Date
  const day = parseInt(parts[2], 10);
  if (isNaN(year) || isNaN(month) || isNaN(day)) return null;
  return new Date(year, month, day);
};

const getLocalYMD = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

export default function SurveyPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [showError, setShowError] = useState(false);
  
  const { 
    groupedQuestions, 
    answers,
    updateAnswer, 
    loading,
    selectedDate,
    setSelectedDate,
    removeAnswer,
    saveSphereAnswers,
  } = useSurvey();

  useEffect(() => {
    const dateFromUrl = searchParams.get('date');
    if (dateFromUrl) {
      const correctedDate = parseYmd(dateFromUrl);
      
      if (correctedDate && !isNaN(correctedDate.getTime())) {
        const contextDateStr = selectedDate ? getLocalYMD(selectedDate) : undefined;
        if (dateFromUrl !== contextDateStr) {
          setSelectedDate(correctedDate);
        }
      }
    }
  }, [searchParams, selectedDate, setSelectedDate]);

  const dateParam = useMemo(() => {
    return selectedDate ? getLocalYMD(selectedDate) : searchParams.get('date');
  }, [selectedDate, searchParams]);

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

  // Вопросы текущей сферы (только базовые для отображения счетчика)
  const questionsInSphere = useMemo(() => {
    const allQuestions = (groupedQuestions[currentSphereId] || []) as any[];
    // Фильтруем только базовые вопросы для отображения счетчика
    // Базовые вопросы имеют ID вида "1.1", "2.3" и т.д., а PRO вопросы имеют ID вида "p1", "g1" и т.д.
    return allQuestions.filter((q: any) => {
      const questionId = String(q.id || '');
      // Базовые вопросы имеют ID с точкой (например, "1.1", "2.3")
      return questionId.includes('.');
    });
  }, [groupedQuestions, currentSphereId]);

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
    console.log('🔍 handleAnswerChange вызвана:', { questionId, value, sphereApiId });
    
    if (sphereApiId === undefined) {
      console.error("Не удалось определить ID сферы для вопроса:", questionId);
      return;
    }
    
    const currentAnswer = answers[questionId];
    const isDeselecting = currentAnswer?.answer === value;
    
    console.log('🔘 Текущий ответ:', currentAnswer, 'isDeselecting:', isDeselecting);

    if (isDeselecting) {
      // Снятие выбора: удаляем ответ (локально и на сервере, если есть id)
      console.log('🔘 Удаляем ответ для вопроса:', questionId);
      removeAnswer(questionId);
    } else {
      // Логика для выбора или изменения ответа
      console.log('🔘 Обновляем ответ:', { questionId, value, sphereApiId });
      updateAnswer({
        question_id: questionId, // Оставляем как строку
        answer: value,
        sphere: Number(sphereApiId),
      });
    }
    
    // Скрываем ошибку при выборе ответа
    setShowError(false);
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
      setShowError(true);
      return false;
    }
    setShowError(false);
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

    // Прокрутка в начало страницы
    window.scrollTo(0, 0);

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

  const swipeHandlers = useSwipe({ onSwipedLeft: handleNext, onSwipedRight: handlePrev });

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
  
  // Проверяем, выбран ли ответ для текущего вопроса
  const currentQuestion = questionsInSphere[currentQuestionIndex] || buildFallbackQuestion(currentSphereId);
  const isAnswerSelected = answers[currentQuestion.id] !== undefined;
  console.log(`🔍 Вопрос ${currentQuestion.id}:`, {
    questionId: currentQuestion.id,
    answerInState: answers[currentQuestion.id],
    isAnswerSelected
  });

  return (
    <div {...swipeHandlers}>
      <ProBasicHeader variant="diagnostics" dateText={selectedDate.toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric' })} />
      <div className={styles.header}>
        <h1 className={styles.pageTitle}>
          <span className={styles.titleIcon}>{sphereIcon}</span>
          {sphereText}
        </h1>
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
                  
                  console.log('🔍 Проверка выбора:', {
                    questionId: q.id,
                    choice,
                    answerValue,
                    currentAnswer: currentAnswer?.answer,
                    isSelected
                  });
                  
                  return (
                    <button
                      key={`${q.id}-${choice}`}
                      type="button"
                      onClick={() => {
                        console.log('🔘 Кнопка нажата:', { questionId: q.id, choice, answerValue, sphereApiId: q.sphere_api_id });
                        handleAnswerChange(q.id, answerValue, q.sphere_api_id ?? Math.max(1, Object.keys(SPHERES).indexOf(q.sphere_id) + 1));
                      }}
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
              {showError && (
                <div className={styles.errorMessage}>
                  Пожалуйста, выберите ответ, прежде чем продолжить
                </div>
              )}
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
        
        {isLastSphere && isLastQuestionInSphere ? (
          <button
            type="button"
            onClick={handleFinish}
            disabled={!isAnswerSelected}
            className={`${styles.finishButton} ${!isAnswerSelected ? styles.disabled : ''}`}
          >
            Завершить
          </button>
        ) : (
          <button
            type="button"
            onClick={handleNext}
            disabled={!isAnswerSelected}
            className={`${styles.navigationButton} ${!isAnswerSelected ? styles.disabled : ''}`}
          >
            Вперед
          </button>
        )}
      </div>
    </div>
  );
}