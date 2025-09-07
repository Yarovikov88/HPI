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

export default function ProSpherePage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { sphereId = SPHERE_ORDERED[0].id } = useParams<{ sphereId: string }>();
  const [showError, setShowError] = useState(false);

  const {
    groupedProQuestions,
    proAnswers,
    updateProAnswerLocal,
    saveProCategoryAnswers,
    loading,
    selectedDate,
    setSelectedDate,
    reloadProAnswers,
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

  const currentSphereIndex = useMemo(() => {
    const index = SPHERE_ORDERED.findIndex(sphere => sphere.id === sphereId);
    return index === -1 ? 0 : index;
  }, [sphereId]);

  const currentSphere = useMemo(() => {
    return SPHERES[sphereId] || SPHERE_ORDERED[0];
  }, [sphereId]);

  // Получаем вопросы для текущей сферы по всем категориям
  const questionsForSphere = useMemo(() => {
    const sphereQuestions: Record<string, any[]> = {};
    
    proCategories.forEach(category => {
      const categoryQuestions = groupedProQuestions[category] || [];
      const sphereQuestionsForCategory = categoryQuestions.filter(q => 
        q.sphere_id === sphereId || q.sphere_api_id === currentSphereIndex + 1
      );
      if (sphereQuestionsForCategory.length > 0) {
        sphereQuestions[category] = sphereQuestionsForCategory;
      }
    });
    
    return sphereQuestions;
  }, [sphereId, currentSphereIndex, groupedProQuestions]);

  // Redirect to the first sphere if the URL is invalid
  useEffect(() => {
    if (!SPHERES[sphereId]) {
      navigate(`/account/pro/sphere/${SPHERE_ORDERED[0].id}`, { replace: true });
    }
  }, [sphereId, navigate]);

  const validateCurrentSphere = () => {
    // Проверяем, что все вопросы в сфере имеют ответы
    const hasAllAnswers = Object.values(questionsForSphere).flat().every(question => {
      const category = question.category;
      const sphereApiId = question.sphere_api_id ?? currentSphereIndex + 1;
      const numericKey = `${category}-${sphereApiId}`;
      
      // Добавляем отладочные логи для валидации
      console.log('🔍 Validation check:', { 
        category, 
        sphereId: question.sphere_id, 
        sphereApiId, 
        numericKey,
        answer: proAnswers[numericKey]
      });
      
      if (category === 'metrics') {
        // Для метрик проверяем, что заполнено текстовое поле
        const answer = proAnswers[numericKey];
        if (!answer) return false;
        
        const text = answer.text || '';
        console.log('�� Metrics validation:', { numericKey, text, isValid: text.trim().length > 0 });
        return text.trim().length > 0;
      } else {
        // Для остальных категорий проверяем текстовое поле
        const answer = proAnswers[numericKey]?.text || '';
        console.log('🔍 Text validation:', { numericKey, answer, isValid: answer.trim().length > 0 });
        return answer.trim().length > 0;
      }
    });
    
    console.log('🔍 Overall validation result:', hasAllAnswers);
    
    if (!hasAllAnswers) {
      setShowError(true);
      return false;
    }
    setShowError(false);
    return true;
  };

  const handleNavigation = (direction: 'next' | 'prev') => {
    if (direction === 'next' && !validateCurrentSphere()) {
      return;
    }
    
    window.scrollTo(0, 0);
    const doNavigate = async () => {
      if (direction === 'next' && saveProCategoryAnswers) {
        console.log('🚀 Начинаем сохранение PRO ответов...');
        // Сохраняем все категории для текущей сферы
        for (const category of Object.keys(questionsForSphere)) {
          console.log(`📤 Сохраняем категорию: ${category}`);
          await saveProCategoryAnswers(category);
        }
        console.log('✅ Все категории сохранены, перезагружаем PRO ответы...');
        // После сохранения перезагружаем ответы из БД, чтобы отобразились галочки
        if (reloadProAnswers) {
          await reloadProAnswers();
          console.log('✅ PRO ответы перезагружены');
        } else {
          console.log('❌ reloadProAnswers не доступна');
        }
      }
      const newIndex = direction === 'next' ? currentSphereIndex + 1 : currentSphereIndex - 1;
      if (newIndex >= 0 && newIndex < SPHERE_ORDERED.length) {
        const newSphereId = SPHERE_ORDERED[newIndex].id;
        navigate(`/account/pro/sphere/${newSphereId}${dateParam ? `?date=${dateParam}` : ''}`);
      } else if (direction === 'next' && newIndex >= SPHERE_ORDERED.length) {
        // Если это была последняя сфера — переходим на PRO дашборд
        navigate(`/account/pro-dashboard${dateParam ? `?date=${dateParam}` : ''}`);
      }
    };
    doNavigate();
  };

  const { handleTouchStart, handleTouchEnd } = useSwipe({
    onSwipeLeft: () => handleNavigation('next'),
    onSwipeRight: () => handleNavigation('prev'),
  });

  if (loading) {
    return <div className={styles.loading}>Загрузка...</div>;
  }

  return (
    <div 
      className={styles.container}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      <ProBasicHeader 
        title={`${currentSphere.emoji} ${currentSphere.name}`}
        subtitle={`${currentSphere.name} - PRO диагностика`}
        currentStep={currentSphereIndex + 1}
        totalSteps={SPHERE_ORDERED.length}
        onBack={() => navigate('/account')}
      />
      {/* Единый заголовок страницы со сферой */}
      <div className={styles.header}>
        <h1 className={styles.pageTitle}>
          <span className={styles.sphereIcon}>{currentSphere?.emoji}</span>
          {currentSphere?.name}
        </h1>
      </div>
      
      <div className={styles.formsContainer}>
        {proCategories.map(category => {
          const categoryQuestions = questionsForSphere[category] || [];
          if (categoryQuestions.length === 0) return null;

          if (category === 'metrics') {
            const metricsQuestion = categoryQuestions[0];
            if (!metricsQuestion) return null;
            
            const metrics = metricsQuestion.metrics || [];
            
            return (
              <div key={category} className={styles.categorySection}>
                <ProMetricsForm
                  sphere={currentSphere}
                  metrics={metrics}
                  answers={proAnswers}
                  onAnswerChange={(metricName, field, value) => {
                    console.log('🔍 ProMetricsForm onChange:', { metricName, field, value });
                    
                    const answerKey = `metrics-${currentSphere.id}`;
                    const currentAnswer = proAnswers[answerKey] || {};
                    
                    // Для нового формата с одним текстовым полем
                    const updatedAnswer = {
                      ...currentAnswer,
                      text: String(value ?? '')  // Сохраняем весь текст как одно поле
                    };
                    
                    console.log('🔍 Updated answer:', updatedAnswer);
                    
                    // Используем правильный формат для updateProAnswerLocal
                    updateProAnswerLocal({
                      sphere_id: currentSphere.id,
                      sphere: currentSphereIndex + 1,
                      ...updatedAnswer
                    }, 'metrics');
                    setShowError(false);
                  }}
                  questionText={metrics[0]?.name}
                  showSphereTitle={false}
                />
              </div>
            );
          }

          return (
            <div key={category} className={styles.categorySection}>
              
              {categoryQuestions.map(question => {
                const sphereInfo = SPHERES[question.sphere_id] || { 
                  id: question.sphere_id, 
                  name: `Сфера ${question.sphere_id}`, 
                  emoji: '❓' 
                };
                
                // Fix: Use only the numeric key that matches what updateProAnswerLocal stores
                const sphereApiId = question.sphere_api_id ?? currentSphereIndex + 1;
                const numericKey = `${category}-${sphereApiId}`;
                
                // Add debug logging
                console.log('🔍 ProQuestionForm retrieval:', { 
                  category, 
                  sphereId: question.sphere_id, 
                  sphereApiId, 
                  numericKey,
                  proAnswers: Object.keys(proAnswers)
                });
                
                const currentAnswer = proAnswers[numericKey]?.text || '';
                console.log('🔍 Retrieved answer:', currentAnswer);

                return (
                  <ProQuestionForm
                    key={`${category}-${question.sphere_id}`}
                    sphere={sphereInfo}
                    answer={currentAnswer}
                    onAnswerChange={(newAnswer) => {
                      console.log('🔍 ProQuestionForm onChange:', { category, sphereApiId, newAnswer });
                      updateProAnswerLocal?.({ sphere: sphereApiId, text: newAnswer }, category);
                      setShowError(false);
                    }}
                    readOnly={false}
                    showSphereTitle={false}
                  />
                );
              })}
            </div>
          );
        })}
      </div>
      
      {showError && (
        <div className={styles.errorMessage}>
          Пожалуйста, заполните все поля, прежде чем продолжить
        </div>
      )}

      <div className={styles.navigationButtons}>
        <button
          className={styles.navButton}
          onClick={() => handleNavigation('prev')}
          disabled={currentSphereIndex === 0}
        >
          ← Назад
        </button>
        
        <button
          className={styles.navButton}
          onClick={() => handleNavigation('next')}
          disabled={false}
        >
          {currentSphereIndex === SPHERE_ORDERED.length - 1 ? 'Завершить' : 'Далее →'}
        </button>
      </div>
    </div>
  );
} 