import { createContext } from 'react';
import type { BasicAnswer, ProAnswer, BasicAnswerPayload, ProAnswerPayload } from '../services/api';

// Единственный источник правды для типа Question
export interface Question {
  id: string;
  text: string;
  options: string[];
  scores: number[];
  category?: string;
  sphere_id: string;
  sphere_api_id?: number;
  sphere?: {
    id: string;
    name: string;
    emoji: string;
  };
  [key: string]: any;
}

export interface SurveyContextType {
  // Состояние
  loading: boolean;
  questions: Question[];
  answers: Record<string, BasicAnswer>;
  proAnswers: Record<string, ProAnswer>;
  groupedQuestions: Record<string, Question[]>;
  groupedProQuestions: Record<string, Question[]>;
  selectedDate: Date;
  setSelectedDate: (date: Date) => void;

  // Методы
  updateAnswer: (payload: Omit<BasicAnswerPayload, 'date'>) => Promise<void>;
  updateProAnswer: (payload: Omit<ProAnswerPayload, 'date'>, category: string) => Promise<void>;
  updateProAnswerLocal?: (payload: Omit<ProAnswerPayload, 'date'>, category: string) => void;
  removeAnswer: (questionId: string) => Promise<void>;
  saveSphereAnswers?: (sphereId: string) => Promise<void>;
  saveProCategoryAnswers?: (category: string) => Promise<void>;

  // Вычисляемые значения и прогресс
  isSphereComplete: (sphereId: string) => boolean;
  isBasicSurveyComplete: boolean;
  getBasicSurveyProgress: () => { answered: number; total: number };
  isProCategoryComplete: (category: string) => boolean;
  isProSurveyComplete: boolean;
  getProSurveyProgress: () => { answered: number; total: number };
}

// Создаем контекст с начальным значением null, чтобы избежать ошибок
export const SurveyContext = createContext<SurveyContextType | null>(null); 