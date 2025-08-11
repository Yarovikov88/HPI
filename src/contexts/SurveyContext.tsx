import React, { 
  useState, 
  useEffect, 
  useMemo, 
  useCallback,
  useRef
} from 'react';
import { apiClient } from '../services/api';
import questionsMock from '../_mocks/questions.json';
import type { BasicAnswer, ProAnswer, ProAnswerPayload, BasicAnswerPayload } from '../services/api';
import { SPHERE_ORDERED } from '../data/spheres';
import { proSections } from '../data/proSections';
// Обновляем импорты, чтобы использовать типы из survey.ts
import { SurveyContext, type SurveyContextType, type Question } from './survey';

// Новая утилита для форматирования даты
const formatDate = (date: Date): string => {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
};

// Создаем карты сопоставления ID сфер
// API может прислать число (1..N) или строку ('love')
const sphereIdMap: Record<number, string> = {};
const sphereNumericMap: Record<string, number> = {};
SPHERE_ORDERED.forEach((sphere, index) => {
  const numeric = index + 1;
  sphereIdMap[numeric] = sphere.id;
  sphereNumericMap[sphere.id] = numeric;
});

// УДАЛЯЕМ ЭТОТ ЛОКАЛЬНЫЙ ТИП, ТАК КАК ОН ТЕПЕРЬ В survey.ts
/*
export type Question = {
  id: string;
  category?: string;
  sphere_id?: string;
  sphere_api_id?: number; // Добавляем это поле
  sphere?: any;
  [key: string]: any;
};
*/

// Локальное хранилище больше не используется для ответов

interface SurveyProviderProps {
    children: React.ReactNode;
}

const SurveyProvider: React.FC<SurveyProviderProps> = ({ children }) => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const questionsRef = useRef(questions);
  questionsRef.current = questions;
  
  const [loading, setLoading] = useState(true);

  // --- Новое состояние для даты ---
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());

  // --- Состояния для ответов ---
  const [answers, setAnswers] = useState<Record<string, BasicAnswer>>({});
  const [proAnswers, setProAnswers] = useState<Record<string, ProAnswer>>({});
  // Запоминаем, для какой даты последней загружали ответы, чтобы корректно решать: мерджить или заменять
  const lastLoadedDateRef = useRef<string | null>(null);
  // Таймеры для дебаунс‑сохранения
  const basicSaveTimersRef = useRef<Record<string, any>>({});
  const proSaveTimersRef = useRef<Record<string, any>>({});
  const removeAnswer = useCallback(async (questionId: string) => {
    try {
      const existing = answers[String(questionId)];
      // Молча игнорируем 404 — значит на сервере уже удалено/не существовало
      if (existing?.id) {
        await apiClient.deleteBasicAnswer(existing.id).catch(() => {});
      }
    } catch (error) {
      console.error('Failed to delete basic answer:', error);
    } finally {
      setAnswers(prev => {
        const copy = { ...prev } as Record<string, BasicAnswer>;
        delete copy[String(questionId)];
        return copy;
      });
    }
  }, [answers]);


  // --- Обновление базового ответа: только локально, без сети ---
  const updateAnswer = useCallback(async (payload: Omit<BasicAnswerPayload, 'date'>) => {
    const safeQuestionId = String(payload.question_id);
    const normalized: BasicAnswer = {
      id: (answers[safeQuestionId]?.id as any) ?? 0,
      question_id: Number(payload.question_id) as any,
      sphere: Number(payload.sphere) as any,
      answer: payload.answer as any,
      date: formatDate(selectedDate),
    };
    setAnswers(prev => ({ ...prev, [safeQuestionId]: normalized }));

    // Дебаунс‑автосохранение одного ответа
    try {
      const timers = basicSaveTimersRef.current;
      if (timers[safeQuestionId]) clearTimeout(timers[safeQuestionId]);
      timers[safeQuestionId] = setTimeout(async () => {
        try {
          await apiClient.upsertBasicAnswer({
            question_id: normalized.question_id as any,
            sphere: normalized.sphere as any,
            answer: normalized.answer,
            date: normalized.date,
          } as any);
        } catch (e) {
          console.error('Auto-save basic failed:', e);
        }
      }, 700);
    } catch {}
  }, [selectedDate, answers]);

  const updateProAnswer = useCallback(async (payload: Omit<ProAnswerPayload, 'date'>, category: string) => {
    // Оптимистичное обновление: сразу показываем введенный текст в контролируемом textarea
    const localDate = formatDate(selectedDate);
    const localSphereKey = sphereIdMap[Number(payload.sphere)] as string;
    const localProAnswerKey = `${category}-${localSphereKey}`;
    const numericKey = `${category}-${String(payload.sphere)}`;
    setProAnswers(prev => ({
      ...prev,
      [localProAnswerKey]: {
        // Если уже есть ответ — сохраняем его id и прочие поля
        id: (prev[localProAnswerKey]?.id as any) ?? 0,
        sphere: Number(payload.sphere) as any,
        text: (payload as any).text ?? '',
        date: localDate,
        category,
      } as ProAnswer,
      [numericKey]: {
        id: (prev[numericKey]?.id as any) ?? ((prev[localProAnswerKey]?.id as any) ?? 0),
        sphere: Number(payload.sphere) as any,
        text: (payload as any).text ?? '',
        date: localDate,
        category,
      } as ProAnswer,
    }));

    try {
      const resp = await apiClient.upsertProAnswer(category, {
        ...payload,
        date: localDate,
      });
      const answerData = Array.isArray(resp) ? resp[0] : resp;
      
      // Ключ для pro-ответа составляется из категории и сферы
      const cat = answerData?.category ?? category;
      const sphereKey = sphereIdMap[Number(answerData?.sphere ?? payload.sphere)] as string;
      const proAnswerKey = `${cat}-${sphereKey}`;
      const proAnswerNumericKey = `${cat}-${String(answerData?.sphere ?? payload.sphere)}`;
      setProAnswers(prev => ({
        ...prev,
        [proAnswerKey]: answerData as ProAnswer,
        [proAnswerNumericKey]: answerData as ProAnswer,
      }));

    } catch (error) {
      console.error("Failed to update pro answer:", error);
      // Опционально: можно откатить локальное состояние или показать тост
    }
  }, [selectedDate]);

  const updateProAnswerLocal = useCallback((payload: Omit<ProAnswerPayload, 'date'>, category: string) => {
    const localDate = formatDate(selectedDate);
    const localSphereKey = sphereIdMap[Number(payload.sphere)] as string;
    const localProAnswerKey = `${category}-${localSphereKey}`;
    const numericKey = `${category}-${String(payload.sphere)}`;
    setProAnswers(prev => ({
      ...prev,
      [localProAnswerKey]: {
        id: (prev[localProAnswerKey]?.id as any) ?? 0,
        sphere: Number(payload.sphere) as any,
        text: (payload as any).text ?? '',
        date: localDate,
        category,
      } as ProAnswer,
      [numericKey]: {
        id: (prev[numericKey]?.id as any) ?? ((prev[localProAnswerKey]?.id as any) ?? 0),
        sphere: Number(payload.sphere) as any,
        text: (payload as any).text ?? '',
        date: localDate,
        category,
      } as ProAnswer,
    }));

    // Дебаунс‑автосохранение одного PRO ответа
    try {
      const timers = proSaveTimersRef.current;
      const timerKey = `${category}-${String(payload.sphere)}`;
      if (timers[timerKey]) clearTimeout(timers[timerKey]);
      timers[timerKey] = setTimeout(async () => {
        try {
          await apiClient.upsertProAnswer(category, {
            sphere: payload.sphere,
            text: (payload as any).text ?? '',
            date: localDate,
          } as any);
        } catch (e) {
          console.error('Auto-save PRO failed:', e);
        }
      }, 700);
    } catch {}
  }, [selectedDate]);

  // Пакетное сохранение ответов по текущей сфере — определим ниже, после groupedQuestions


  const basicQuestions = useMemo(() => questions.filter(q => !q.category), [questions]);

  const groupedQuestions = useMemo(() => {
    const groups: Record<string, Question[]> = {};
    basicQuestions.forEach(q => {
      const sphereId = q.sphere_id; // уже строковый id
      if (sphereId) {
        if (!groups[sphereId]) groups[sphereId] = [];
        groups[sphereId].push(q);
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
    // Проверяем, есть ли ответ для каждого вопроса в сфере
    return groupedQuestions[sphereId].every(q => answers[q.id]);
  }, [groupedQuestions, answers]);

  const isBasicSurveyComplete = useMemo(() => {
    const sphereIds = Object.keys(groupedQuestions);
    if (sphereIds.length === 0) return false;
    return sphereIds.every(isSphereComplete);
  }, [groupedQuestions, isSphereComplete]);


  // --- Pro Survey State ---
  const proQuestions = useMemo(() => questions.filter(q => q.category), [questions]);
  
  const groupedProQuestions = useMemo(() => {
    const categories: Record<string, Question[]> = {};
    proSections.forEach(section => {
      categories[section.category] = proQuestions.filter(q => q.category === section.category);
    });
    return categories;
  }, [proQuestions]);

  const getProSurveyProgress = useCallback(() => {
    const totalSteps = Object.keys(groupedProQuestions).length;
    const answeredSteps = Object.values(groupedProQuestions).filter(group => {
        // Проверяем, есть ли ответ для каждого вопроса в категории
        return group.every(q => proAnswers[`${q.category}-${q.sphere_id}`]);
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
    // Проверяем, есть ли ответ для каждого вопроса в категории
    return questionsForCategory.every(q => {
      const answer = proAnswers[`${category}-${q.sphere_id}`];
      return answer && answer.text.trim() !== '';
    });
  }, [groupedProQuestions, proAnswers]);

  // Пакетное сохранение PRO-ответов по категории
  const saveProCategoryAnswers = useCallback(async (category: string) => {
    try {
      // Дата сохранения: приоритет у ?date= из URL
      const params = new URLSearchParams(window.location.search);
      const dateFromUrl = params.get('date');
      const dateToSave = dateFromUrl && dateFromUrl.length === 10 ? dateFromUrl : formatDate(selectedDate);
      const questionsForCategory = groupedProQuestions[category] || [];
      const payloads = questionsForCategory
        .map(q => {
          const key = `${category}-${q.sphere_id}`;
          const ans = proAnswers[key];
          if (!ans || !ans.text?.trim()) return null;
          // найти numeric sphere
          const numeric = sphereNumericMap[q.sphere_id];
          return {
            id: (ans.id as any) ?? undefined,
            sphere: (ans.sphere as any) || (numeric as any),
            text: ans.text,
            date: dateToSave,
          } as ProAnswerPayload;
        })
        .filter(Boolean) as ProAnswerPayload[];

      if (payloads.length > 0) {
        await apiClient.saveProAnswers(category, payloads);
      }
    } catch (error) {
      console.error('Failed to batch save pro category answers:', error);
    }
  }, [groupedProQuestions, proAnswers, selectedDate]);

  // Пакетное сохранение ответов по текущей сфере
  const saveSphereAnswers = useCallback(async (sphereId: string) => {
    try {
      const questionsInSphere = groupedQuestions[sphereId] || [];
      const payloads = questionsInSphere
        .map((q) => answers[q.id])
        .filter((ans): ans is BasicAnswer => Boolean(ans))
        .map((ans) => ({
          // сервер принимает строки; типы клиента нестрого соответствуют, приведём через unknown
          question_id: String(ans.question_id) as unknown as number,
          sphere: String(ans.sphere) as unknown as number,
          answer: ans.answer,
          date: formatDate(selectedDate),
        }));
      if (payloads.length > 0) {
        // @ts-ignore
        const saved = await apiClient.saveBasicAnswers(payloads as any);
        // Обновляем локально id сохранённых ответов
        if (Array.isArray(saved)) {
          setAnswers((prev) => {
            const next = { ...prev } as Record<string, BasicAnswer>;
            saved.forEach((a: any) => {
              const key = String(a.question_id);
              next[key] = { ...next[key], ...a } as BasicAnswer;
            });
            return next;
          });
        }
      }
    } catch (error) {
      console.error('Failed to batch save sphere answers:', error);
    }
  }, [groupedQuestions, answers, selectedDate]);

  // --- Data Fetching (Переработано) ---

  // 1. Эффект для загрузки ВОПРОСОВ (один раз при монтировании)
  useEffect(() => {
    const fetchQuestions = async () => {
      setLoading(true);
      try {
        // Гарантируем наличие токена перед запросами к защищённым эндпоинтам
        const existingToken = localStorage.getItem('authToken');
        if (!existingToken) {
          await apiClient.telegramAuth();
        }

        // ИСПРАВЛЯЕМ ОШИБКУ: apiClient.getSurvey -> [apiClient.getQuestions, apiClient.getProQuestions]
        const [basicQuestionsData, proQuestionsData] = await Promise.all([
          apiClient.getQuestions(),
          apiClient.getProQuestions()
        ]);

        // Бэкенд возвращает массив объектов по сферам: [{ sphere: number, questions: Question[] }, ...]
        const basicArray: any[] = Array.isArray(basicQuestionsData)
          ? (basicQuestionsData as any[]).flatMap((group: any) =>
              (group?.questions || []).map((q: any) => ({ ...q, sphere: group?.sphere }))
            )
          : [];

        const proArray: any[] = Array.isArray(proQuestionsData)
          ? (proQuestionsData as any[]).flat()
          : [];

        // Преобразуем базовые вопросы: добавляем sphere_id (строковый) и sphere_api_id (числовой), нормализуем поля текста/опций
        const mappedBasicQuestions: Question[] = (basicArray || []).map((q: any) => {
          // Определяем сферу
          const sphereApiIdFromNumber = typeof q.sphere === 'number' ? q.sphere : (typeof q.sphere_api_id === 'number' ? q.sphere_api_id : undefined);
          const sphereIdFromString = typeof q.sphere === 'string' ? q.sphere : undefined;
          const sphereApiId: number | undefined = sphereApiIdFromNumber ?? (sphereIdFromString ? sphereNumericMap[sphereIdFromString] : undefined);
          const sphereId: string | undefined = sphereIdFromString ?? (sphereApiId ? sphereIdMap[sphereApiId] : undefined);

          // Нормализуем текст/опции/баллы
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
          } as Question;
        });

        // Преобразуем PRO-вопросы: нормализуем sphere_id и sphere_api_id
        const mappedProQuestions: Question[] = (proArray || []).map((q: any) => {
          const sphereApiId: number | undefined =
            typeof q.sphere === 'number' ? q.sphere : (typeof q.sphere_id === 'number' ? q.sphere_id : undefined);
          const sphereId: string | undefined =
            typeof q.sphere === 'number' ? sphereIdMap[q.sphere] : (typeof q.sphere_id === 'number' ? sphereIdMap[q.sphere_id] : (typeof q.sphere === 'string' ? q.sphere : undefined));

          return {
            ...q,
            category: q.category,
            sphere_id: sphereId as string,
            sphere_api_id: sphereApiId as number | undefined,
          } as Question;
        });

        let combined = mappedBasicQuestions.concat(mappedProQuestions);

        // Fallback: если базовых вопросов нет, используем моки
        if (mappedBasicQuestions.length === 0 && Array.isArray(questionsMock)) {
          const mockBasic = (questionsMock as any[])
            .filter((q) => q.type === 'basic')
            .map((q) => {
              const sphereIdFromString = typeof q.sphere === 'string' ? q.sphere : undefined;
              const sphereApiId = sphereIdFromString ? sphereNumericMap[sphereIdFromString] : undefined;
              const normalizedText: string = q.text ?? '';
              const optionsSource: any = q.options;
              const fallbackOptions = ['Совсем нет', 'Скорее нет', 'Скорее да', 'Полностью да'];
              const normalizedOptions: string[] = Array.isArray(optionsSource) && optionsSource.length > 0 ? optionsSource : fallbackOptions;
              const normalizedScores: number[] = Array.isArray(q.scores) && q.scores.length === normalizedOptions.length
                ? q.scores
                : Array.from({ length: normalizedOptions.length }, (_, i) => i + 1);
              return {
                id: String(q.id ?? `${sphereIdFromString}-${normalizedText.slice(0, 8)}`),
                text: normalizedText,
                options: normalizedOptions,
                scores: normalizedScores,
                sphere_id: sphereIdFromString,
                sphere_api_id: sphereApiId,
              } as Question;
            });
          combined = mockBasic.concat(mappedProQuestions);
        }

        setQuestions(combined);
      } catch (error) {
        console.error("Failed to fetch survey questions:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchQuestions();
  }, []);

  // 2. Эффект для загрузки ответов (при изменении selectedDate)
  useEffect(() => {
    const loadAnswers = async () => {
      try {
        const date = formatDate(selectedDate);
        // Сразу очищаем PRO-ответы при смене даты, чтобы не показывать предыдущие значения
        setProAnswers({});

        // Базовые ответы -> словарь по question_id (строка)
        const basicAnswerList = await apiClient.getBasicAnswers(date);
        const basicAnswersDict = (basicAnswerList || []).reduce<Record<string, BasicAnswer>>((acc, ans) => {
          const key = String(ans.question_id);
          const prev = acc[key];
          if (!prev) {
            acc[key] = ans;
          } else {
            const prevCreated = prev.created_at ?? '';
            const currCreated = ans.created_at ?? '';
            // выбираем самый новый по created_at
            acc[key] = currCreated > prevCreated ? ans : prev;
          }
          return acc;
        }, {});
        setAnswers(basicAnswersDict);

        // PRO ответы загружаем по категориям и собираем в один словарь
        const categories = proSections.map(s => s.category);
        const proLists = await Promise.all(
          categories.map(category => apiClient.getProAnswers(category, date).catch(() => [] as ProAnswer[]))
        );
        // Добавляем недостающую категорию, если сервер не возвращает её в ответе
        const proAnswersDict = proLists
          .map((list, idx) => list.map(ans => ({ ...ans, category: ans.category ?? categories[idx] })))
          .flat()
          .reduce<Record<string, ProAnswer>>((acc, ans) => {
            const cat = ans.category as string;
            const sphereKeyStr = sphereIdMap[Number(ans.sphere as any)] as string | undefined;
            const keyByString = sphereKeyStr ? `${cat}-${sphereKeyStr}` : undefined;
            const keyByNumeric = `${cat}-${String(ans.sphere)}`;
            if (keyByString) acc[keyByString] = ans as ProAnswer;
            acc[keyByNumeric] = ans as ProAnswer;
            return acc;
          }, {});
        setProAnswers(proAnswersDict);
        lastLoadedDateRef.current = date;
      } catch (error) {
        console.error("Failed to load answers:", error);
      }
    };

    loadAnswers();
  }, [selectedDate]);

  // 3. Сохранять не нужно пакетно: upsert выполняется при updateAnswer/updateProAnswer

  // 4. Эффект для сохранения ответов при размонтировании
  useEffect(() => {
    return () => {
      // Сохраняем ответы при размонтировании, если пользователь закрыл страницу
      // Этот эффект может быть полезен, если пользователь закрыл страницу,
      // но не успел сохранить ответы.
      // Однако, в текущей реализации, сохранение происходит при каждом изменении selectedDate.
      // Поэтому, если пользователь закрыл страницу, ответы не будут сохранены.
      // Для полной функциональности, потребуется другой механизм сохранения.
    };
  }, []);

  const contextValue: SurveyContextType = {
    questions,
    loading,
    selectedDate,
    setSelectedDate,
    answers,
    updateAnswer,
    removeAnswer,
    saveSphereAnswers,
    proAnswers,
    updateProAnswer,
    updateProAnswerLocal,
    groupedQuestions,
    groupedProQuestions,
    getBasicSurveyProgress,
    isBasicSurveyComplete,
    getProSurveyProgress,
    isProSurveyComplete,
    isProCategoryComplete,
    isSphereComplete,
    saveProCategoryAnswers,
  };

  return (
    <SurveyContext.Provider value={contextValue}>
      {children}
    </SurveyContext.Provider>
  );
};

export default SurveyProvider;