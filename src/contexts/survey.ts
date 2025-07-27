import React, { createContext } from 'react';
// import type { Question as ApiQuestion } from '../services/api';

export type Sphere = {
    id: string;
    name: string;
    emoji: string;
}

export type Question = { // Omit<ApiQuestion, 'sphere_id'> & {
    sphere?: Sphere;
    id: string; // Добавим id, так как он используется в коде
};

export type SurveyContextType = {
  questions: Question[];
  loading: boolean;
  
  // Basic Survey
  answers: Record<string, string | number>;
  setAnswers: React.Dispatch<React.SetStateAction<Record<string, string | number>>>;
  updateAnswer: (questionId: string, answer: string | number) => void;
  removeAnswer: (questionId: string) => void;
  groupedQuestions: Record<string, Question[]>;
  isSphereComplete: (sphereId: string) => boolean;
  isBasicSurveyComplete: boolean;
  getBasicSurveyProgress: () => { answered: number, total: number };
  
  // Pro Survey
  proAnswers: Record<string, any>;
  setProAnswers: React.Dispatch<React.SetStateAction<Record<string, any>>>;
  updateProAnswer: (questionId: string, answer: any) => void;
  proQuestions: Question[];
  groupedProQuestions: Record<string, Question[]>;
  isProStepComplete: (stepIndex: number) => boolean;
  isProSurveyComplete: boolean;
  getProSurveyProgress: () => { answered: number, total: number };
  isProCategoryComplete: (category: string) => boolean;
  
  // Actions
  fillAllWithMockData: () => void;
  refetchAllData: () => Promise<void>;
  setAnswersFromApi: (answersFromApi: any[]) => void;
}

export const SurveyContext = createContext<SurveyContextType | undefined>(undefined); 