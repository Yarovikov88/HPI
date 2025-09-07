import React, { 
  useState, 
  useEffect, 
  useMemo, 
  useCallback,
  useRef
} from 'react';
import { apiClient } from '../services/api';
import questionsMock from '../_mocks/questions.json';
import { SPHERE_ORDERED } from '../data/spheres';
import { proSections } from '../data/proSections';
// Импортируем SurveyContext из survey.ts
import { SurveyContext } from './survey';
import { useAuth } from '../hooks/useAuth';

// Простые типы прямо здесь
interface Question {
  id: string;
  text: string;
  options: string[];
  scores: number[];
  category?: string;
  sphere_id: string;
  sphere_api_id?: number;
  sphere?: any;
  [key: string]: any;
}

interface ProAnswer {
  id: number;
  sphere: number | string;
  text: string;
  date: string;
  category: string;
  created_at?: string;
  what_measure?: string;
  target_value?: number;
  unit?: string;
}

interface BasicAnswer {
  id: number;
  question_id: string; // Исправляем: должен быть строкой
  sphere: number;
  answer: string; // Исправляем: должен быть строкой для консистентности
  date: string;
  created_at?: string;
}

interface SurveyContextType {
  loading: boolean;
  questions: Question[];
  answers: Record<string, BasicAnswer>;
  proAnswers: Record<string, ProAnswer>;
  groupedQuestions: Record<string, Question[]>;
  groupedProQuestions: Record<string, Question[]>;
  selectedDate: Date;
  setSelectedDate: (date: Date) => void;
  proCompletionStatus: any;
  updateAnswer: (payload: any) => Promise<void>;
  updateProAnswer: (payload: any, category: string) => Promise<void>;
  updateProAnswerLocal?: (payload: any, category: string) => void;
  removeAnswer: (questionId: string) => Promise<void>;
  saveSphereAnswers?: (sphereId: string) => Promise<void>;
  saveProCategoryAnswers?: (category: string) => Promise<void>;
  reloadProAnswers?: () => Promise<void>;
  loadProCompletionStatus?: () => Promise<void>;
  isSphereComplete: (sphereId: string) => boolean;
  isBasicSurveyComplete: boolean;
  getBasicSurveyProgress: () => { answered: number; total: number };
  isProCategoryComplete: (category: string) => boolean;
  isProSphereComplete: (sphereId: string) => boolean; // Добавляем новую функцию
  isProSurveyComplete: boolean;
  getProSurveyProgress: () => { answered: number; total: number };
  isLoadingAnswers: boolean;
  isDataReady: boolean;
  refreshCurrentDate: () => Promise<void>;
}

// Создаем контекст
// export const SurveyContext = createContext<SurveyContextType | null>(null);

// Новая утилита для форматирования даты
const formatDate = (date: Date): string => {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
};

// Создаем карты сопоставления ID сфер
const sphereIdMap: Record<number, string> = {};
const sphereNumericMap: Record<string, number> = {};
SPHERE_ORDERED.forEach((sphere, index) => {
  const numeric = index + 1;
  sphereIdMap[numeric] = sphere.id;
  sphereNumericMap[sphere.id] = numeric;
});

interface SurveyProviderProps {
  children: any;
}

const SurveyProvider = ({ children }: SurveyProviderProps) => {
  const { user } = useAuth(); // Добавляем получение user из useAuth
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [answersLoading, setAnswersLoading] = useState(true);

  // Инициализация выбранной даты из URL (?date=YYYY-MM-DD) до первой загрузки
  const initialSelectedDate = useMemo(() => {
    try {
      const params = new URLSearchParams(window.location.search);
      const d = params.get('date');
      if (d) {
        const parsed = new Date(d);
        if (!isNaN(parsed.getTime())) return parsed;
      }
    } catch {}
    return new Date();
  }, []);

  const [selectedDate, setSelectedDate] = useState<Date>(initialSelectedDate);
  const [answers, setAnswers] = useState<Record<string, BasicAnswer>>({});
  const [proAnswers, setProAnswers] = useState<Record<string, ProAnswer>>({});
  const [proCompletionStatus, setProCompletionStatus] = useState<any>(null);
  // Добавляем состояние для отслеживания загрузки
  const [isLoadingAnswers, setIsLoadingAnswers] = useState(false);
  // Флаг, чтобы не загружать вопросы повторно (StrictMode/ремонты эффекта)
  const questionsLoadedRef = useRef(false);
  // Идентификатор активной загрузки ответов, чтобы игнорировать старые ответы
  const activeLoadIdRef = useRef(0);

  // Добавляем ref для отслеживания последней загруженной даты
  const lastLoadedDateRef = useRef<string | null>(null);

  // Объявляем loadProAnswers в начале, до использования
  const loadProAnswers = useCallback(async () => {
    if (!user) return {};
    
    try {
      console.log('🔄 SurveyContext: Загружаем PRO ответы');
      const proAnswers: Record<string, ProAnswer> = {};
      
      const categories = ['problems', 'goals', 'blockers', 'metrics', 'achievements'];
      const date = selectedDate.toISOString().split('T')[0];
      
      for (const category of categories) {
        try {
          const answers = await apiClient.getProAnswers(category, date);
          answers.forEach(answer => {
            const key = `${category}-${answer.sphere_id}`;
            proAnswers[key] = answer;
          });
        } catch (error) {
          console.error(`❌ SurveyContext: Ошибка загрузки PRO ответов для ${category}:`, error);
        }
      }
      
      console.log(' SurveyContext: PRO ответы загружены:', proAnswers);
      return proAnswers;
    } catch (error) {
      console.error('❌ SurveyContext: Ошибка загрузки PRO ответов:', error);
      return {};
    }
  }, [selectedDate]);

  // Простая логика для загрузки вопросов
  useEffect(() => {
    let isMounted = true;
    // Используем ref, чтобы избежать повторной загрузки в StrictMode
    
    const fetchQuestions = async () => {
      // Если уже загружали, пропускаем
      if (questionsLoadedRef.current || questions.length > 0) {
        console.log('🔄 SurveyContext: Вопросы уже загружены, пропускаем');
        return;
      }
      questionsLoadedRef.current = true;
      
      try {
        console.log('🔄 SurveyContext: Начинаем загрузку вопросов');
        setLoading(true);
        
        // Гарантируем наличие токена
        const existingToken = localStorage.getItem('authToken');
        if (!existingToken) {
          console.log(' SurveyContext: Токен не найден, запрашиваем Telegram auth');
          await apiClient.telegramAuth();
        }

        console.log('🔄 SurveyContext: Загружаем базовые и PRO вопросы');
        // Загружаем базовые и PRO вопросы
        const [basicQuestionsData, proQuestionsData] = await Promise.all([
          apiClient.getQuestions('ru').catch((error) => {
            console.error('❌ SurveyContext: Ошибка загрузки базовых вопросов:', error);
            return [];
          }),
          Promise.all([
            apiClient.getProQuestions('problems', 'ru').catch(() => []),
            apiClient.getProQuestions('goals', 'ru').catch(() => []),
            apiClient.getProQuestions('blockers', 'ru').catch(() => []),
            apiClient.getProQuestions('metrics', 'ru').catch(() => []),
            apiClient.getProQuestions('achievements', 'ru').catch(() => [])
          ]).then(results => results.flat()).catch(() => [])
        ]);
        
        if (!isMounted) return;
        
        console.log(' SurveyContext: Базовые вопросы загружены:', basicQuestionsData);
        console.log(' SurveyContext: PRO вопросы загружены:', proQuestionsData);
        
        // Обрабатываем базовые вопросы
        let basicArray: any[] = [];
        if (Array.isArray(basicQuestionsData)) {
          const arr = basicQuestionsData as any[];
          const looksGrouped = arr.length > 0 && Array.isArray((arr[0] as any)?.questions);
          
          if (looksGrouped) {
            basicArray = arr.flatMap((group: any) =>
              (group?.questions || []).map((q: any) => ({ ...q, sphere: group?.sphere }))
            );
          } else {
            basicArray = arr.map((q: any) => {
              let sphereNum: number | undefined =
                typeof q.sphere === 'number'
                  ? q.sphere
                  : (typeof q.sphere_api_id === 'number' ? q.sphere_api_id : undefined);
              if (sphereNum == null && q?.id != null) {
                const m = String(q.id).match(/^(\d+)[\._-]/);
                if (m) sphereNum = Number(m[1]);
              }
              return { ...q, sphere: sphereNum };
            });
          }
        }

        // Обрабатываем PRO вопросы
        const proArray: any[] = Array.isArray(proQuestionsData)
          ? (proQuestionsData as any[]).flat()
          : [];

        // Преобразуем базовые вопросы
        const mappedBasicQuestions: Question[] = (basicArray || []).map((q: any) => {
          let sphereApiId: number | undefined =
            typeof q.sphere === 'number'
              ? q.sphere
              : (typeof q.sphere_api_id === 'number' ? q.sphere_api_id : undefined);

          let sphereId: string | undefined =
            typeof q.sphere === 'string' && isNaN(Number(q.sphere))
              ? q.sphere
              : undefined;

          if (sphereApiId == null && q?.id != null) {
            const m = String(q.id).match(/^(\d+)[\._-]/);
            if (m) sphereApiId = Number(m[1]);
          }
          if (sphereApiId == null && typeof q.sphere === 'string' && /^\d+$/.test(q.sphere)) {
            sphereApiId = Number(q.sphere);
          }
          if (!sphereId && sphereApiId != null) {
            sphereId = sphereIdMap[sphereApiId];
          }

          const normalizedText: string = q.text ?? q.title ?? q.name ?? q.question_text ?? q.description ?? '';
          const optionsSource: any = q.options ?? q.choices ?? q.labels ?? q.variants;
          const fallbackOptions = ['Совсем нет', 'Скорее нет', 'Скорее да', 'Полностью да'];
          const normalizedOptions: string[] = Array.isArray(optionsSource) && optionsSource.length > 0 ? optionsSource : fallbackOptions;
          const scoresSource: any = q.scores;
          const normalizedScores: number[] = Array.isArray(scoresSource) && scoresSource.length === normalizedOptions.length
            ? scoresSource
            : Array.from({ length: normalizedOptions.length }, (_, i) => i + 1);

          return {
            ...q,
            id: String(q.id ?? q.question_id ?? `${sphereId || 'unknown'}-${normalizedText.slice(0, 8)}`),
            text: normalizedText,
            options: normalizedOptions,
            scores: normalizedScores,
            sphere_id: sphereId as string,
            sphere_api_id: sphereApiId as number | undefined,
            category: undefined
          } as Question;
        });

        // Преобразуем PRO вопросы (как раньше)
        const mappedProQuestions: Question[] = (proArray || []).map((q: any) => {
          let sphereApiId: number | undefined =
            typeof q.sphere === 'number'
              ? q.sphere
              : (typeof q.sphere_api_id === 'number' ? q.sphere_api_id : undefined);
          let sphereId: string | undefined =
            typeof q.sphere_id === 'string' ? q.sphere_id : undefined;
          if (!sphereId && sphereApiId != null) sphereId = sphereIdMap[sphereApiId];

          const normalizedText: string = q.text ?? q.title ?? q.name ?? q.question_text ?? q.description ?? '';
          const optionsSource: any = q.options ?? q.choices ?? q.labels ?? q.variants;
          const fallbackOptions = ['Совсем нет', 'Скорее нет', 'Скорее да', 'Полностью да'];
          const normalizedOptions: string[] = Array.isArray(optionsSource) && optionsSource.length > 0 ? optionsSource : fallbackOptions;
          const scoresSource: any = q.scores;
          const normalizedScores: number[] = Array.isArray(scoresSource) && scoresSource.length === normalizedOptions.length
            ? scoresSource
            : Array.from({ length: normalizedOptions.length }, (_, i) => i + 1);

          // Парсим fields для метрик
          let metrics: any[] = [];
          try {
            const fields = q.fields || q.meta || q.schema;
            const parsed = typeof fields === 'string' ? JSON.parse(fields) : fields;
            if (parsed?.metrics && Array.isArray(parsed.metrics)) metrics = parsed.metrics;
          } catch {}

          return {
            ...q,
            id: String(q.id ?? q.question_id ?? `${sphereId || 'unknown'}-${normalizedText.slice(0, 8)}`),
            text: normalizedText,
            options: normalizedOptions,
            scores: normalizedScores,
            sphere_api_id: sphereApiId,
            sphere_id: sphereId || 'unknown',
            metrics,
          } as Question;
        });

        const groupedBasic: Record<string, Question[]> = {};
        (mappedBasicQuestions || []).forEach((q) => {
          const cat = 'basic';
          groupedBasic[cat] = groupedBasic[cat] || [];
          groupedBasic[cat].push(q);
        });

        const groupedPro: Record<string, Question[]> = {};
        (mappedProQuestions || []).forEach((q: any) => {
          const cat = (q.category || 'problems') as string;
          groupedPro[cat] = groupedPro[cat] || [];
          groupedPro[cat].push(q);
        });

        console.log('🔄 SurveyContext: Устанавливаем вопросы:', [...mappedBasicQuestions, ...mappedProQuestions]);
        setQuestions([...mappedBasicQuestions, ...mappedProQuestions]);
        // setGroupedQuestions(groupedBasic); // This line was removed as per the new_code
        // setGroupedProQuestions(groupedPro); // This line was removed as per the new_code

        setLoading(false);
        console.log('✅ SurveyContext: Загрузка завершена успешно');
      } catch (error) {
        console.error('❌ SurveyContext: Ошибка загрузки вопросов:', error);
          setLoading(false);
      }

      return () => { isMounted = false; };
    };

    fetchQuestions();
  }, [questions.length]);

  // Метод для загрузки статуса завершения PRO опроса
  const loadProCompletionStatus = useCallback(async () => {
    try {
      const date = formatDate(selectedDate);
      console.log('🔄 Загружаем статус завершенности для даты:', date);
      const status = await apiClient.getProCompletionStatus(date);
      console.log('📊 Статус завершенности PRO опроса:', status);
      console.log('📊 Структура spheres:', status?.spheres);
      console.log('📊 Общий статус завершенности:', status?.overall_complete);
      console.log('📊 Завершенные сферы:', status?.completed_spheres);
      console.log('📊 Всего сфер:', status?.total_spheres);
      setProCompletionStatus(status);
    } catch (e) {
      console.error('❌ Ошибка при загрузке статуса завершенности:', e);
    }
  }, [selectedDate]);

  const loadAnswersCore = useCallback(async () => {
      if (!user) return;
      
      const date = selectedDate.toISOString().split('T')[0];
      
    // Инкрементируем идентификатор загрузки
    const loadId = ++activeLoadIdRef.current;
    // Очищаем прошлые данные, чтобы не мигали ответы другой даты
    setAnswers({});
    setProAnswers({});
    setProCompletionStatus(null as any);
      try {
        console.log('🔄 SurveyContext: Загружаем ответы пользователя для даты:', date);
        setAnswersLoading(true);
        
        // Базовые ответы
        const basicAnswerList = await apiClient.getBasicAnswers(date);
        const basicAnswersDict = (basicAnswerList || []).reduce((acc: Record<string, BasicAnswer>, ans: any) => {
          const key = String(ans.question_id);
          acc[key] = ans;
          return acc;
        }, {});

        // PRO ответы - используем исправленную логику
        const categories = proSections.map(s => s.category);
        const proLists = await Promise.all(
          categories.map(category => apiClient.getProAnswers(category, date).catch(() => [] as ProAnswer[]))
        );
        
        console.log('📥 Загружаем PRO ответы с сервера:', proLists);
        
        const proAnswersDict = proLists
          .map((list: any[], idx: number) => list.map((ans: any) => ({ ...ans, category: ans.category ?? categories[idx] })))
          .flat()
          .reduce<Record<string, ProAnswer>>((acc: Record<string, ProAnswer>, ans: any) => {
            const cat = ans.category as string;
            const sphereId = ans.sphere_id || ans.sphere;
            const sphereKeyStr = sphereIdMap[Number(sphereId)] as string | undefined;
            const keyByString = sphereKeyStr ? `${cat}-${sphereKeyStr}` : undefined;
            const keyByNumeric = `${cat}-${String(sphereId)}`;
            if (keyByString) acc[keyByString] = ans as ProAnswer;
            acc[keyByNumeric] = ans as ProAnswer;
            console.log(`🔑 Создаем ключи для ответа: ${cat}, sphere: ${sphereId}, stringKey: ${keyByString}, numericKey: ${keyByNumeric}`);
            return acc;
          }, {});
        
      // Если это уже не актуальная загрузка — выходим
      if (loadId !== activeLoadIdRef.current) {
        console.log('⏭️ Пропускаем устаревший результат загрузки для даты:', date);
        return;
      }

        setAnswers(basicAnswersDict);
        setProAnswers(proAnswersDict);
        
      // Также загрузим статус завершенности для даты
        try {
        console.log('🔄 Загружаем статус завершенности для даты:', date);
          const status = await apiClient.getProCompletionStatus(date);
          console.log('📊 Статус завершенности PRO опроса:', status);
          setProCompletionStatus(status);
        } catch (e) {
          console.error('❌ Ошибка при загрузке статуса завершенности:', e);
        }
    } catch (e) {
      console.error('❌ Ошибка загрузки дашборда:', e);
      } finally {
        setAnswersLoading(false);
      }
  }, [selectedDate, user]);

  // Загружаем ответы пользователя при изменении даты
  useEffect(() => {
    loadAnswersCore();
  }, [loadAnswersCore]);

  const refreshCurrentDate = useCallback(async () => {
    await loadAnswersCore();
  }, [loadAnswersCore]);

  // Простые вычисляемые значения
  const basicQuestions = useMemo(() => {
    return questions.filter((q: Question) => !q.category);
  }, [questions]);

  const groupedQuestions = useMemo(() => {
    const groups: Record<string, Question[]> = {};
    basicQuestions.forEach((q: Question) => {
      if (q.sphere_id) {
        if (!groups[q.sphere_id]) groups[q.sphere_id] = [];
        groups[q.sphere_id].push(q);
      }
    });
    return groups;
  }, [basicQuestions]);

  const groupedProQuestions = useMemo(() => {
    const categories: Record<string, Question[]> = {};
    proSections.forEach(section => {
      categories[section.category] = questions.filter((q: Question) => q.category === section.category);
    });
    return categories;
  }, [questions]);

  // Простые методы
  const updateAnswer = useCallback(async (payload: any) => {
    console.log('updateAnswer called with:', payload);
    
    // Обновляем локальное состояние
    setAnswers(prev => ({
      ...prev,
      [payload.question_id]: {
        id: prev[payload.question_id]?.id || Date.now(),
        question_id: payload.question_id, // Оставляем как строку
        sphere: Number(payload.sphere), // Преобразуем в число
        answer: String(payload.answer), // Исправляем: сохраняем как строку для консистентности
        date: selectedDate.toISOString().split('T')[0],
        created_at: prev[payload.question_id]?.created_at || new Date().toISOString()
      }
    }));
    
    // Отправляем на сервер
    try {
      const dataToSend = [{
        question_id: payload.question_id, // Отправляем как строку (сервер ожидает str)
        sphere: Number(payload.sphere),
        answer: String(payload.answer), // Исправляем: отправляем как строку
        date: selectedDate.toISOString().split('T')[0]
      }];
      
      console.log('📤 Отправляем на сервер:', dataToSend);
      console.log('📤 Детали данных:', {
        question_id: dataToSend[0].question_id,
        question_id_type: typeof dataToSend[0].question_id,
        sphere: dataToSend[0].sphere,
        sphere_type: typeof dataToSend[0].sphere,
        answer: dataToSend[0].answer,
        answer_type: typeof dataToSend[0].answer,
        date: dataToSend[0].date
      });
      await apiClient.postBasicAnswers(dataToSend);
      console.log('✅ Ответ успешно сохранен на сервере');
    } catch (error) {
      console.error('❌ Ошибка сохранения ответа:', error);
    }
  }, [selectedDate]);

  const updateProAnswer = useCallback(async (payload: any, category: string) => {
    // Простая реализация
    console.log('updateProAnswer called with:', payload, category);
  }, []);

  const updateProAnswerLocal = useCallback((payload: any, category: string) => {
    // Локальное обновление состояния
    console.log('🔄 updateProAnswerLocal called with:', payload, category);
    
    // Для метрик нужно использовать sphere_id из payload, а не sphere
    let stringKey, numericKey;
    
    if (category === 'metrics' && payload.sphere_id) {
      // Для метрик используем sphere_id (строку)
      stringKey = `${category}-${payload.sphere_id}`;
      numericKey = `${category}-${String(payload.sphere)}`;
    } else {
      // Для остальных категорий используем sphere (число)
      stringKey = `${category}-${payload.sphere}`;
      numericKey = `${category}-${String(payload.sphere)}`;
    }
    
    console.log('🔑 Keys:', { stringKey, numericKey });
    
    setProAnswers(prev => {
      const newAnswer = {
        ...prev[stringKey] || prev[numericKey] || {},
        ...payload,
        id: (prev[stringKey] || prev[numericKey])?.id || Date.now(),
        created_at: (prev[stringKey] || prev[numericKey])?.created_at || new Date().toISOString()
      };
      
      const newState = {
        ...prev,
        [stringKey]: newAnswer,
        [numericKey]: newAnswer
      };
      
      console.log('📝 New proAnswers state:', newState);
      return newState;
    });
  }, []);

  const removeAnswer = useCallback(async (questionId: string) => {
    // Простая реализация
    console.log('removeAnswer called with:', questionId);
  }, []);

  const isSphereComplete = useCallback((sphereId: string) => {
    if (!groupedQuestions[sphereId]) return false;
    const allQuestions = groupedQuestions[sphereId];
    const basicQuestions = allQuestions.filter((q: Question) => String(q.id).includes('.'));
    const firstSixBasicQuestions = basicQuestions.slice(0, 6);
    return firstSixBasicQuestions.length === 6 && firstSixBasicQuestions.every((q: Question) => {
      const answer = answers[q.id];
      return answer && answer.answer !== undefined && answer.answer !== null && answer.answer !== '';
    });
  }, [groupedQuestions, answers]);

  const isBasicSurveyComplete = useMemo(() => {
    const sphereIds = Object.keys(groupedQuestions);
    if (sphereIds.length === 0) return false;
    return sphereIds.every(isSphereComplete);
  }, [groupedQuestions, isSphereComplete]);

  const getBasicSurveyProgress = useCallback(() => {
    const totalQuestions = basicQuestions.length;
    const answeredQuestions = Object.keys(answers).filter(qId => {
      const answer = answers[qId];
      return answer && answer.answer !== undefined && answer.answer !== null && answer.answer !== '';
    }).length;
    return { answered: answeredQuestions, total: totalQuestions };
  }, [answers, basicQuestions]);

  const isProCategoryComplete = useCallback((category: string) => {
    // Используем статус из backend если доступен
    if (proCompletionStatus && proCompletionStatus.spheres) {
      // Проверяем все сферы для данной категории
      return Object.values(proCompletionStatus.spheres).every((sphere: any) => {
        const categoryData = sphere.categories[category];
        return categoryData && categoryData.has_answer;
      });
    }
    return false; // Fallback
  }, [proCompletionStatus]);

  const isProSurveyComplete = useMemo(() => {
    // Используем статус из backend если доступен
    if (proCompletionStatus) {
      return proCompletionStatus.overall_complete;
    }
    return false; // Fallback
  }, [proCompletionStatus]);

  const getProSurveyProgress = useCallback(() => {
    // Используем статус из backend если доступен
    if (proCompletionStatus) {
      return { 
        answered: proCompletionStatus.completed_spheres, 
        total: proCompletionStatus.total_spheres 
      };
    }
    return { answered: 0, total: 0 }; // Fallback
  }, [proCompletionStatus]);

  const saveSphereAnswers = useCallback(async (sphereId: string) => {
    // Простая реализация
    console.log('saveSphereAnswers called with:', sphereId);
  }, []);

  const saveProCategoryAnswers = useCallback(async (category: string) => {
    console.log('saveProCategoryAnswers called with:', category);
    
    try {
      // Находим все ответы для данной категории
      const categoryAnswers = Object.entries(proAnswers)
        .filter(([key, answer]) => key.startsWith(`${category}-`))
        .map(([key, answer]) => answer);
      
      console.log(`📤 Сохраняем ${categoryAnswers.length} ответов для категории ${category}:`, categoryAnswers);
      
      // Отправляем каждый ответ на сервер
      for (const answer of categoryAnswers) {
        if (answer && answer.text) {
          try {
            console.log(`🚀 Отправляем ответ на сервер:`, answer);
            
            // Всегда создаем новый ответ через postProAnswer
            const response = await apiClient.postProAnswer(category, {
              sphere: answer.sphere,
              text: answer.text,
              date: answer.date || formatDate(selectedDate)
            });
            console.log(`✅ Создан ответ для ${category}:`, response);
          } catch (error) {
            console.error(`❌ Ошибка при сохранении ответа для ${category}:`, error);
          }
        }
      }
    } catch (error) {
      console.error(`❌ Ошибка при сохранении категории ${category}:`, error);
    }
  }, [proAnswers, selectedDate]);

  const reloadProAnswers = useCallback(async () => {
    console.log('reloadProAnswers called');
    
    try {
      const date = formatDate(selectedDate);
      
      // Загружаем PRO ответы
      const categories = proSections.map(s => s.category);
      const proLists = await Promise.all(
        categories.map(category => apiClient.getProAnswers(category, date).catch(() => [] as ProAnswer[]))
      );
      
      const proAnswersDict = proLists
        .map((list: any[], idx: number) => list.map((ans: any) => ({ ...ans, category: ans.category ?? categories[idx] })))
        .flat()
        .reduce<Record<string, ProAnswer>>((acc: Record<string, ProAnswer>, ans: any) => {
          const cat = ans.category as string;
          const sphereKeyStr = sphereIdMap[Number(ans.sphere as any)] as string | undefined;
          const keyByString = sphereKeyStr ? `${cat}-${sphereKeyStr}` : undefined;
          const keyByNumeric = `${cat}-${String(ans.sphere)}`;
          if (keyByString) acc[keyByString] = ans as ProAnswer;
          acc[keyByNumeric] = ans as ProAnswer;
          return acc;
        }, {});
      
      setProAnswers(proAnswersDict);
      console.log('✅ PRO ответы перезагружены:', proAnswersDict);
      
      // Загружаем статус завершенности после перезагрузки ответов
      await loadProCompletionStatus();
    } catch (error) {
      console.error('❌ Ошибка при перезагрузке PRO ответов:', error);
    }
  }, [selectedDate, loadProCompletionStatus]);

  const isProSphereComplete = useCallback((sphereId: string) => {
    console.log('🔍 isProSphereComplete: Проверяем сферу', sphereId);
    console.log('🔍 isProSphereComplete: proCompletionStatus', proCompletionStatus);
    
    // Используем статус из backend если доступен
    if (proCompletionStatus && proCompletionStatus.spheres) {
      console.log('🔍 isProSphereComplete: Доступные ключи в spheres:', Object.keys(proCompletionStatus.spheres));
      
      // Создаем маппинг строковых ID на числовые
      const sphereIdMapping: Record<string, number> = {
        'love': 1,
        'family': 2,
        'friends': 3,
        'career': 4,
        'physical': 5,
        'mental': 6,
        'hobby': 7,
        'wealth': 8
      };
      
      const numericId = sphereIdMapping[sphereId];
      console.log('🔍 isProSphereComplete: numericId для', sphereId, '=', numericId);
      
      if (numericId) {
        const sphereKey = `sphere_${numericId}`;
        const sphereData = proCompletionStatus.spheres[sphereKey];
        console.log('🔍 isProSphereComplete: sphereKey', sphereKey);
        console.log('🔍 isProSphereComplete: sphereData', sphereData);
        
        if (sphereData && sphereData.is_complete === true) {
          console.log('🔍 isProSphereComplete: is_complete', sphereData.is_complete);
          return true;
        }

        // Фоллбек: локально проверяем заполненность всех категорий по ответам
        const categories: string[] = ['problems', 'goals', 'blockers', 'metrics', 'achievements'];
        const allFilledLocally = categories.every((cat) => {
          const answer = proAnswers?.[`${cat}-${numericId}`];
          if (!answer) return false;
          // Для metrics допускаем либо text, либо поля what_measure/target_value/unit
          if (cat === 'metrics') {
            const hasText = typeof (answer as any).text === 'string' && (answer as any).text.trim().length > 0;
            const hasStructured = Boolean((answer as any).what_measure) || typeof (answer as any).target_value === 'number' || Boolean((answer as any).unit);
            return hasText || hasStructured;
          }
          return typeof (answer as any).text === 'string' && (answer as any).text.trim().length > 0;
        });

        if (allFilledLocally) {
          console.log('✅ isProSphereComplete: локальный фоллбек считает сферу завершенной');
          return true;
        }
      } else {
        console.log('🔍 isProSphereComplete: Не найден numericId для', sphereId);
      }
    }
    console.log('🔍 isProSphereComplete: Fallback - false');
    return false; // Fallback
  }, [proCompletionStatus, proAnswers]);

  const contextValue: SurveyContextType = {
    loading,
    questions,
    answers,
    proAnswers,
    groupedQuestions,
    groupedProQuestions,
    selectedDate,
    setSelectedDate,
    proCompletionStatus,
    updateAnswer,
    updateProAnswer,
    updateProAnswerLocal,
    removeAnswer,
    saveSphereAnswers,
    saveProCategoryAnswers,
    reloadProAnswers,
    loadProCompletionStatus,
    isSphereComplete,
    isBasicSurveyComplete,
    getBasicSurveyProgress,
    isProCategoryComplete,
    isProSphereComplete, // Добавляем новую функцию
    isProSurveyComplete,
    getProSurveyProgress,
    isLoadingAnswers,
    isDataReady: !isLoadingAnswers && !!proCompletionStatus,
    refreshCurrentDate
  };

  return (
    <SurveyContext.Provider value={contextValue}>
      {children}
    </SurveyContext.Provider>
  );
};

export default SurveyProvider;