import { NavLink, useLocation } from 'react-router-dom';
import { useSurvey } from '../hooks/useSurvey';
import styles from './ProBasicHeader.module.css';

interface ProBasicHeaderProps {
  variant?: 'dashboards' | 'diagnostics';
  dateText?: string;
}

export const ProBasicHeader: React.FC<ProBasicHeaderProps> = ({ variant = 'dashboards', dateText }) => {
  const location = useLocation();
  const { isBasicSurveyComplete, isProSurveyComplete } = useSurvey();

  const isProActive = location.pathname.includes('/pro');
  const isBasicActive = !isProActive;

  const basicButtonClasses = `${styles.button} ${isBasicActive ? styles.active : ''} ${!isBasicSurveyComplete ? styles.disabled : ''}`;
  const proButtonClasses = `${styles.button} ${isProActive ? styles.active : ''} ${!isProSurveyComplete ? styles.disabled : ''}`;

  const handleBasicClick = (e: React.MouseEvent) => {
    if (!isBasicSurveyComplete) {
      e.preventDefault();
      alert('Для доступа к базовому дашборду необходимо завершить базовую диагностику.');
      return;
    }
  };

  const handleProClick = (e: React.MouseEvent) => {
    if (!isProSurveyComplete) {
      e.preventDefault();
      alert('Для доступа к PRO дашборду необходимо завершить PRO диагностику.');
      return;
    }
  };

  // If on diagnostics pages, render indicators (not clickable) + centered date
  if (variant === 'diagnostics') {
    return (
      <div className={styles.header}>
        <div className={`${styles.button} ${isBasicActive ? styles.active : ''}`}>
          Базовый
        </div>
        <div className={`${styles.button} ${isProActive ? styles.active : ''}`}>
          Pro
        </div>
        {dateText && <div className={styles.dateCenter}>{dateText}</div>}
      </div>
    );
  }

  // If on dashboards pages, render clickable NavLinks
  return (
    <div className={styles.header}>
      <NavLink to="/account/dashboard" className={basicButtonClasses} onClick={handleBasicClick}>
        Базовый
      </NavLink>
      <NavLink to="/account/pro-dashboard" className={proButtonClasses} onClick={handleProClick}>
        Pro
      </NavLink>
      {dateText && <div className={styles.dateRight}>{dateText}</div>}
    </div>
  );
}; 