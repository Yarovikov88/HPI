import { createContext } from 'react';
import type { SurveyContextType } from './types';

// Создаем контекст с начальным значением null, чтобы избежать ошибок
export const SurveyContext = createContext<SurveyContextType | null>(null);

// Реэкспортируем типы для обратной совместимости
export type { Question, ProAnswer, SurveyContextType } from './types'; 