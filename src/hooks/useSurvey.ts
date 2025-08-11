import { useContext } from 'react';
import { SurveyContext } from '../contexts/survey';

export const useSurvey = () => {
  const context = useContext(SurveyContext);
  // Заменяем проверку с undefined на null
  if (context === null) {
    throw new Error('useSurvey must be used within a SurveyProvider');
  }
  return context;
}; 