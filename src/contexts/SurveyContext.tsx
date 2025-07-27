import React, { 
  useState, 
  useEffect, 
  useMemo, 
  useCallback,
  useRef
} from 'react';
// import { apiClient } from '../services/api';
import mockQuestions from '../_mocks/questions.json'; // Импортируем моковые данные
import { SPHERES } from '../data/spheres';
import { SurveyContext, type SurveyContextType } from './survey';

// Добавляем недостающие поля в тип Question локально
export type Question = {
  id: string;
  category?: string;
  sphere_id?: string;
  sphere?: any;
  [key: string]: any;
};

const ANSWERS_KEY = 'surveyAnswers';
const PRO_ANSWERS_KEY = 'proSurveyAnswers';

interface SurveyProviderProps {
    children: React.ReactNode;
}

const SurveyProvider: React.FC<SurveyProviderProps> = ({ children }) => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const questionsRef = useRef(questions);
  questionsRef.current = questions;
  
  const [loading, setLoading] = useState(true);

  // --- Basic Survey State ---
  const [answers, setAnswers] = useState<Record<string, string | number>>({});

  const updateAnswer = useCallback((questionId: string, answer: string | number) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  }, []);

  const removeAnswer = useCallback((questionId: string) => {
    setAnswers(prev => {
      const newAnswers = { ...prev };
      delete newAnswers[questionId];
      return newAnswers;
    });
  }, []);

  const basicQuestions = useMemo(() => questions.filter(q => !q.category), [questions]);

  const groupedQuestions = useMemo(() => {
    const groups: Record<string, Question[]> = {};
    basicQuestions.forEach(q => {
      if (q.sphere?.id) {
        if (!groups[q.sphere.id]) groups[q.sphere.id] = [];
        groups[q.sphere.id].push(q);
      }
    });
    return groups;
  }, [basicQuestions]);
  
  const getBasicSurveyProgress = useCallback(() => {
    const totalQuestions = basicQuestions.length;
    const answeredQuestions = Object.keys(answers).filter(qId => basicQuestions.some(q => q.id === qId)).length;
    return { answered: answeredQuestions, total: totalQuestions };
  }, [answers, basicQuestions]);

  const isSphereComplete = useCallback((sphereId: string) => {
    if (!groupedQuestions[sphereId]) return false;
    return groupedQuestions[sphereId].every(q => answers[q.id] !== undefined);
  }, [groupedQuestions, answers]);

  const isBasicSurveyComplete = useMemo(() => {
    const sphereIds = Object.keys(groupedQuestions);
    if (sphereIds.length === 0) return false;
    return sphereIds.every(isSphereComplete);
  }, [groupedQuestions, isSphereComplete]);


  // --- Pro Survey State ---
  const [proAnswers, setProAnswers] = useState<Record<string, string>>({});

  // ИЗМЕНЕНО: answer теперь имеет тип string
  const updateProAnswer = useCallback((questionId: string, answer: string) => {
    setProAnswers(prev => ({ ...prev, [questionId]: answer }));
  }, []);

  const proQuestions = useMemo(() => questions.filter(q => q.category), [questions]);
  
  const groupedProQuestions = useMemo(() => {
    const categories: Record<string, Question[]> = {
      problems: proQuestions.filter(q => q.category === 'problems'),
      goals: proQuestions.filter(q => q.category === 'goals'),
      blockers: proQuestions.filter(q => q.category === 'blockers'),
      metrics: proQuestions.filter(q => q.category === 'metrics'),
      achievements: proQuestions.filter(q => q.category === 'achievements'),
    };
    return categories;
  }, [proQuestions]);

  const getProSurveyProgress = useCallback(() => {
    const totalSteps = Object.keys(groupedProQuestions).length;
    const answeredSteps = Object.values(groupedProQuestions).filter(group => {
        return group.every(q => proAnswers[q.id] !== undefined && proAnswers[q.id] !== '');
    }).length;
    return { answered: answeredSteps, total: totalSteps };
  }, [proAnswers, groupedProQuestions]);

  const isProSurveyComplete = useMemo(() => {
    const progress = getProSurveyProgress();
    return progress.total > 0 && progress.answered === progress.total;
  }, [getProSurveyProgress]);

  const isProCategoryComplete = useCallback((category: string) => {
    const questionsForCategory = groupedProQuestions[category];
    if (!questionsForCategory || questionsForCategory.length === 0) {
      return false;
    }
    // ОБНОВЛЕННАЯ ЛОГИКА
    return questionsForCategory.every(q => {
      const answer = proAnswers[q.id];
      if (answer === undefined || answer === null) return false;
      // Для метрик проверяем, что это не пустой объект
      if (category === 'metrics') {
        return typeof answer === 'object' && Object.keys(answer).length > 0;
      }
      // Для остальных - проверяем, что строка не пустая
      return typeof answer === 'string' && answer.trim() !== '';
    });
  }, [groupedProQuestions, proAnswers]);

  // --- Data Fetching and Actions ---

  const refetchAllData = useCallback(async () => {
    setLoading(true);
    try {
      // const rawQuestions = await apiClient.getQuestions(); // Временно отключаем
      const rawQuestions = mockQuestions as Question[]; // Используем моковые данные
      const allQuestions = rawQuestions.map((q: Question) => ({
        ...q,
        sphere: q.sphere_id ? SPHERES[q.sphere_id] : undefined
      }));
      setQuestions(allQuestions as any);

      // Обработка базовых ответов
      const newAnswersState: Record<string, number> = {};
      // todaysAnswers.forEach(answer => { // Временно отключаем
      //   newAnswersState[answer.question_id] = answer.answer;
      // });
      setAnswers(newAnswersState);

      // Обработка Pro-ответов - пока отключаем, так как данных нет
      setProAnswers({});
      /*
      if (todaysProData && typeof todaysProData === 'object' && !Array.isArray(todaysProData)) {
        const proDataTyped = todaysProData as Record<string, any[]>;
        const categories: string[] = ['problems', 'goals', 'blockers', 'achievements'];
        
        categories.forEach(category => {
          if (proDataTyped[category]) {
            proDataTyped[category].forEach((item: any) => {
              const question = allQuestions.find(q => q.sphere_id === item.sphere_id && q.category === category);
              if (question) {
                newProAnswersState[question.id] = item.description || item.text;
              }
            });
          }
        });
        
        if (proDataTyped.metrics) {
          proDataTyped.metrics.forEach((metric: any) => {
            const question = allQuestions.find(q => q.sphere_id === metric.sphere_id && q.category === 'metrics');
            if (question) {
              if (!newProAnswersState[question.id]) {
                newProAnswersState[question.id] = {};
              }
              newProAnswersState[question.id][metric.name] = {
                current_value: metric.current_value,
                target_value: metric.target_value,
              };
            }
          });
        }
      }

      setProAnswers(newProAnswersState);
      */
    } catch (e) {
      console.error("Ошибка при загрузке данных опросов:", e);
      setAnswers({});
      setProAnswers({});
    } finally {
      setLoading(false);
    }
  }, []);
  
  useEffect(() => {
    refetchAllData();
  }, [refetchAllData]);

  const setAnswersFromApi = useCallback((answersFromApi: any[]) => {
    const newAnswersState: Record<string, number> = {};
    answersFromApi.forEach(answer => {
      newAnswersState[answer.question_id] = answer.answer;
    });
    setAnswers(newAnswersState);
  }, []);

  // Dummy function
  const fillAllWithMockData = useCallback(() => {}, []);
  const isProStepComplete = useCallback(() => false, []);


  const value = useMemo(() => ({
    questions,
    loading,
    answers,
    setAnswers,
    updateAnswer,
    removeAnswer,
    groupedQuestions,
    isSphereComplete,
    isBasicSurveyComplete,
    getBasicSurveyProgress,
    proAnswers,
    setProAnswers,
    updateProAnswer,
    proQuestions,
    groupedProQuestions,
    isProStepComplete,
    isProSurveyComplete,
    getProSurveyProgress,
    fillAllWithMockData,
    refetchAllData,
    setAnswersFromApi,
    isProCategoryComplete,
  }), [
    questions,
    loading,
    answers,
    proAnswers,
    groupedQuestions,
    isSphereComplete,
    isBasicSurveyComplete,
    getBasicSurveyProgress,
    proQuestions,
    groupedProQuestions,
    isProStepComplete,
    isProSurveyComplete,
    getProSurveyProgress,
    updateAnswer,
    removeAnswer,
    updateProAnswer,
    refetchAllData,
    setAnswersFromApi,
    isProCategoryComplete
  ]);
  
  return <SurveyContext.Provider value={value}>{children}</SurveyContext.Provider>;
};

export default SurveyProvider;