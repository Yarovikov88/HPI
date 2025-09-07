import type { BasicAnswer, BasicAnswerPayload, ProAnswerPayload } from '../services/api';

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

export interface ProAnswer {
	id: number;
	sphere: number | string;
	text: string;
	date: string;
	category: string;
	created_at?: string;
	// Дополнительные поля для метрик
	what_measure?: string;
	target_value?: number;
	unit?: string;
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
  proCompletionStatus: any; // Новое поле для статуса завершения

  // Методы
  updateAnswer: (payload: Omit<BasicAnswerPayload, 'date'>) => Promise<void>;
  updateProAnswer: (payload: Omit<ProAnswerPayload, 'date'>, category: string) => Promise<void>;
  updateProAnswerLocal?: (payload: Omit<ProAnswerPayload, 'date'>, category: string) => void;
  removeAnswer: (questionId: string) => Promise<void>;
  saveSphereAnswers?: (sphereId: string) => Promise<void>;
  saveProCategoryAnswers?: (category: string) => Promise<void>;
  reloadProAnswers?: () => Promise<void>;
  loadProCompletionStatus?: () => Promise<void>; // Новый метод

  // Вычисляемые значения и прогресс
  isSphereComplete: (sphereId: string) => boolean;
  isBasicSurveyComplete: boolean;
  getBasicSurveyProgress: () => { answered: number; total: number };
  isProCategoryComplete: (category: string) => boolean;
  isProSurveyComplete: boolean;
  getProSurveyProgress: () => { answered: number; total: number };
} 