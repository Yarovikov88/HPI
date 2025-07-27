import { useContext } from 'react';
import { SurveyContext } from '../contexts/survey';

export const useSurvey = () => {
  const context = useContext(SurveyContext);
  if (context === undefined) {
    throw new Error('useSurvey must be used within a SurveyProvider');
  }
  return context;
}; 