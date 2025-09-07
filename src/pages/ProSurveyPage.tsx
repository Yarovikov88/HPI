import React, { useMemo, useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useSurvey } from '../hooks/useSurvey';
import ProQuestionForm from '../components/ProQuestionForm';
import ProMetricsForm from '../components/ProMetricsForm';
import { SPHERES, SPHERE_ORDERED } from '../data/spheres';
import styles from './ProSurveyPage.module.css';
import { useSwipe } from '../hooks/useSwipe';
import { ProBasicHeader } from '../components/ProBasicHeader';

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
  
  // Получаем категорию из URL пути или параметров
  const pathCategory = location.pathname.split('/').pop();
  const { category: paramCategory } = useParams<{ category: string }>();
  const category = paramCategory || pathCategory || proCategories[0];
  
  const [showError, setShowError] = useState(false);
  const [currentSphereIndex, setCurrentSphereIndex] = useState(0);
  const [isSaving, setIsSaving] = useState(false);

  const {
    groupedProQuestions,
    groupedQuestions, // Добавляем доступ к базовым вопросам
    proAnswers,
    updateProAnswerLocal,
    saveProCategoryAnswers,
    loading,
    selectedDate,
    setSelectedDate,
  } = useSurvey();

  const searchParams = new URLSearchParams(location.search);
  const dateParam = searchParams.get('date');
  const getLocalYMD = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  const todayStr = getLocalYMD(new Date());
  const isToday = !dateParam || dateParam === todayStr;

  useEffect(() => {
    if (dateParam) {
      const d = new Date(dateParam);
      if (!Number.isNaN(d.getTime())) {
        const ctx = selectedDate ? getLocalYMD(selectedDate) : undefined;
        if (ctx !== dateParam) setSelectedDate(d);
      }
    }
  }, [dateParam, setSelectedDate, selectedDate]);

  const currentCategoryIndex = useMemo(() => {
    const index = proCategories.indexOf(category);
    return index === -1 ? 0 : index;
  }, [category]);

  // Текущая сфера
  const currentSphere = SPHERE_ORDERED[currentSphereIndex];

  // Отладочная информация
  console.log('🔍 ProSurveyPage Debug:', {
    currentSphereIndex,
    currentSphere,
    category,
    currentCategoryIndex,
    SPHERE_ORDERED: SPHERE_ORDERED.map(s => ({ id: s.id, name: s.name })),
    totalSpheres: SPHERE_ORDERED.length,
    proAnswers
  });

  // Создаем вопросы для текущей сферы по всем категориям
  const currentSphereQuestions = useMemo(() => {
    return proCategories.map(cat => ({
      sphere_id: currentSphere.id,
      sphere_api_id: currentSphereIndex + 1,
      category: cat,
      text: `Опишите ваши ${categoryTranslations[cat]?.toLowerCase() || cat} в сфере "${currentSphere.name}"`,
      sphere: currentSphere
    }));
  }, [currentSphere, currentSphereIndex]);

  // Redirect to the first category if the URL is invalid
  useEffect(() => {
    if (!proCategories.includes(category)) {
      navigate(`/account/pro/${proCategories[0]}`, { replace: true });
    }
  }, [category, navigate]);

  // Принудительно обновляем состояние при загрузке
  useEffect(() => {
    console.log('🔄 ProSurveyPage mounted/updated:', {
      category,
      currentSphereIndex,
      currentSphere: currentSphere?.name
    });
  }, [category, currentSphereIndex, currentSphere]);

  const validateCurrentSphere = () => {
    // Проверяем ВСЕ категории, у которых есть вопросы для текущей сферы
    const categoriesToCheck = proCategories;
    for (const cat of categoriesToCheck) {
      const list = groupedProQuestions[cat] || [];
      const sphereQs = list.filter(q => q.sphere_id === currentSphere.id || q.sphere_api_id === currentSphereIndex + 1);
      if (sphereQs.length === 0) continue; // если вопросов нет — пропускаем категорию

      // Для каждой категории должны быть непустые ответы
      const sphereApiId = currentSphereIndex + 1;
      const numericKey = `${cat}-${sphereApiId}`;

      if (cat === 'metrics') {
        const answer = proAnswers[numericKey];
        const text = (answer?.text || '').trim();
        if (text.length === 0) return false;
      } else {
        const text = (proAnswers[numericKey]?.text || '').trim();
        if (text.length === 0) return false;
      }
    }
    return true;
  };

  const hasAllAnswers = validateCurrentSphere();

  const handleNavigation = async (direction: 'prev' | 'next') => {
    console.log('🚀 handleNavigation вызван:', { direction, currentSphereIndex, currentSphere: currentSphere?.name });
    
    if (direction === 'prev') {
      if (currentSphereIndex > 0) {
        // Переходим к предыдущей сфере
        setCurrentSphereIndex(currentSphereIndex - 1);
      }
    } else if (direction === 'next') {
      console.log('📋 Проверяем валидность текущей сферы...');
      console.log('✅ hasAllAnswers:', hasAllAnswers);
      console.log('📊 proAnswers для текущей сферы:', Object.keys(proAnswers).filter(k => k.includes(currentSphere?.id || '')));
      
      // Сначала сохраняем все ответы для текущей сферы
      setIsSaving(true);
      try {
        console.log('💾 Сохраняем ответы для сферы:', currentSphere?.name);
        
        // Сохраняем ответы для каждой категории текущей сферы
        for (const cat of proCategories) {
          const proAnswerKey = `${cat}-${currentSphere.id}`;
          const numericKey = `${cat}-${String(currentSphereIndex + 1)}`;
          
          console.log(` Проверяем категорию ${cat}:`, { proAnswerKey, numericKey });
          
          if (cat === 'metrics') {
            // Для метрик проверяем, что есть данные для сохранения
            const answer = proAnswers[proAnswerKey] || proAnswers[numericKey];
            console.log(`📊 Ответ для метрик ${cat}:`, answer);
            
            if (answer && answer.text) {
              console.log(`📊 Сохраняем метрики для ${cat}:`, answer.text);
              await saveProCategoryAnswers?.(cat);
            } else {
              console.log(`⚠️ Нет данных для сохранения метрик ${cat}`);
            }
          } else {
            // Для остальных категорий проверяем, что есть текстовый ответ
            const answer = proAnswers[proAnswerKey]?.text || proAnswers[numericKey]?.text;
            console.log(`📝 Ответ для ${cat}:`, answer);
            
            if (answer && answer.trim().length > 0) {
              console.log(`📝 Сохраняем ответ для ${cat}:`, answer);
              await saveProCategoryAnswers?.(cat);
            } else {
              console.log(`⚠️ Нет данных для сохранения ${cat}`);
            }
          }
        }
        
        console.log('✅ Ответы для сферы сохранены');
        
        // Теперь переходим к следующей сфере или завершаем
        if (currentSphereIndex < SPHERE_ORDERED.length - 1) {
          setCurrentSphereIndex(currentSphereIndex + 1);
        } else {
          // Завершаем опрос
          console.log('🏁 PRO опрос завершен, переходим к дашборду');
          navigate('/account/dashboard');
        }
      } catch (error) {
        console.error('❌ Ошибка при сохранении ответов:', error);
        setShowError(true);
      } finally {
        setIsSaving(false);
      }
    }
  };

  const swipeHandlers = useSwipe({
    onSwipedLeft: () => handleNavigation('next'),
    onSwipedRight: () => handleNavigation('prev'),
  });

  if (loading) {
    return (
      <div className={styles.container}>
        <ProBasicHeader variant="dashboards" dateText={selectedDate.toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric' })} />
        <div className={styles.loading}>Загрузка...</div>
      </div>
    );
  }

  return (
    <div className={styles.container} {...swipeHandlers}>
      <ProBasicHeader variant="dashboards" dateText={selectedDate.toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric' })} />
      
      <div className={styles.header}>
        <h1 className={styles.pageTitle}>
          <span className={styles.sphereIcon}>{currentSphere?.emoji}</span>
          {currentSphere?.name || 'Загрузка...'}
        </h1>
        <div className={styles.categoryTitle}>
          Все категории для текущей сферы
        </div>
        <div className={styles.progress}>
          Сфера {currentSphereIndex + 1} из {SPHERE_ORDERED.length}
        </div>
      </div>
      
      <div className={styles.formsContainer}>
        {currentSphere ? (
          // Показываем ВСЕ 5 категорий для текущей сферы
          proCategories.map(cat => {
            if (cat === 'metrics') {
              // Получаем вопрос метрик для текущей сферы из Pro вопросов
              const metricsQuestions = groupedProQuestions['metrics'] || [];
              const sphereMetricsQuestion = metricsQuestions.find(q => 
                q.sphere_id === currentSphere.id || q.sphere_api_id === currentSphereIndex + 1
              );
              
              return (
                <div key={`metrics-${currentSphere.id}`} className={styles.categorySection}>
                  <h3 className={styles.categoryTitle}>{categoryTranslations[cat]}</h3>
                  
                  {sphereMetricsQuestion ? (
                    (() => {
                      const metricsList = (sphereMetricsQuestion as any).metrics || (sphereMetricsQuestion as any).fields?.metrics || [];
                      return (
                        <ProMetricsForm
                          sphere={currentSphere}
                          metrics={metricsList}
                          answers={proAnswers}
                          questionText={metricsList[0]?.name}
                          showSphereTitle={false}
                          onAnswerChange={(metricName: string, field: string, value: any) => {
                            console.log('🎯 ProSurveyPage onAnswerChange for metrics:', {
                              metricName,
                              field,
                              value,
                              currentSphereId: currentSphere.id,
                              currentSphereIndex,
                              proAnswers
                            });
                            
                            const proAnswerKey = `metrics-${currentSphere.id}`;
                            const numericKey = `metrics-${String(currentSphereIndex + 1)}`;
                            const currentAnswer = proAnswers[proAnswerKey] || proAnswers[numericKey] || {};
                            
                            console.log('🔍 Current answer keys:', { proAnswerKey, numericKey, currentAnswer });
                            
                            // Сохраняем простой текст без JSON-обёртки
                            const newAnswer = {
                              ...currentAnswer,
                              sphere: currentSphereIndex + 1,
                              sphere_id: currentSphere.id,
                              category: 'metrics',
                              text: String(value ?? ''),
                              date: selectedDate.toISOString().split('T')[0]
                            } as any;
                            
                            console.log(' New answer to save:', newAnswer);
                            
                            updateProAnswerLocal?.(newAnswer, 'metrics');
                            setShowError(false);
                          }}
                        />
                      );
                    })()
                  ) : (
                    <div className={styles.noQuestionMessage}>
                      Вопросы метрик для сферы "{currentSphere.name}" не найдены
                    </div>
                  )}
                </div>
              );
            } else {
              // Остальные категории остаются без изменений
              const categoryQuestions = groupedProQuestions[cat] || [];
              const questionsForSphere = categoryQuestions.filter(q => 
                q.sphere_id === currentSphere.id || q.sphere_api_id === currentSphereIndex + 1
              );

              return (
                <div key={`${cat}-${currentSphere.id}`} className={styles.categorySection}>
                  <h3 className={styles.categoryTitle}>{categoryTranslations[cat]}</h3>
                  
                  {questionsForSphere.length > 0 ? (
                    (() => {
                      const sphereApiId = currentSphereIndex + 1;
                      const numericKey = `${cat}-${sphereApiId}`;
                      const currentAnswer = proAnswers[numericKey]?.text || '';
                      return (
                        <ProQuestionForm
                          sphere={{ id: currentSphere.id as any, name: currentSphere.name as any, emoji: (currentSphere as any).emoji as any }}
                          answer={currentAnswer}
                          onAnswerChange={(text: string) => {
                            updateProAnswerLocal?.({ sphere: sphereApiId, text, category: cat }, cat);
                            setShowError(false);
                          }}
                          showSphereTitle={false}
                        />
                      );
                    })()
                  ) : (
                    <div className={styles.noQuestionMessage}>
                      Вопросы для категории "{categoryTranslations[cat]}" не найдены
                    </div>
                  )}
                </div>
              );
            }
          })
        ) : (
          <div className={styles.errorMessage}>
            Сфера не найдена
          </div>
        )}
      </div>
      
      {showError && (
        <div className={styles.errorMessage}>
          Пожалуйста, заполните все поля, прежде чем продолжить
        </div>
      )}

      <div className={styles.navigationButtons}>
        <button onClick={() => handleNavigation('prev')} disabled={currentSphereIndex === 0}>
          Назад
        </button>
        <button 
          onClick={() => handleNavigation('next')}
          disabled={!hasAllAnswers || isSaving}
          className={!hasAllAnswers || isSaving ? styles.disabled : ''}
        >
          {isSaving ? 'Сохранение...' : currentSphereIndex === SPHERE_ORDERED.length - 1 ? 'Завершить' : 'Далее'}
        </button>
      </div>
    </div>
  );
}