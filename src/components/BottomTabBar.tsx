import { Link, useLocation } from 'react-router-dom';
import styles from './BottomTabBar.module.css';
import { FaPoll, FaTh, FaCalendarAlt } from 'react-icons/fa';
import { useSurvey } from '../hooks/useSurvey';

const tabs = [
  { path: '/account/diagnostics', icon: <FaPoll />, label: 'Диагностика', matchPaths: ['/account/diagnostics', '/account/survey', '/account/pro-survey'] },
  { path: '/account/dashboard', icon: <FaTh />, label: 'Дашборд', matchPaths: ['/account/dashboard', '/account/pro-dashboard'] },
  { path: '/account/calendar', icon: <FaCalendarAlt />, label: 'История', matchPaths: ['/account/calendar'] },
];

export const BottomTabBar = () => {
  const location = useLocation();
  const { isBasicSurveyComplete } = useSurvey();
  const params = new URLSearchParams(location.search);
  const date = params.get('date');
  const dateSuffix = date ? `?date=${date}` : '';

  const isTabActive = (tab: typeof tabs[0]) => {
    return tab.matchPaths.some(path => location.pathname.startsWith(path));
  };

  const handleTabClick = (tab: typeof tabs[0], e: React.MouseEvent) => {
    // Если это дашборд и диагностика не завершена, блокируем переход
    if (tab.path.includes('/dashboard') && !isBasicSurveyComplete) {
      e.preventDefault();
      // Можно добавить уведомление пользователю
      alert('Для доступа к дашборду необходимо завершить базовую диагностику.');
      return;
    }
  };

  return (
    <nav className={styles.bottomTabBar}>
      {tabs.map(tab => (
        <Link
          key={tab.path}
          to={`${tab.path}${dateSuffix}`}
          className={`${styles.tab} ${isTabActive(tab) ? styles.active : ''} ${tab.path.includes('/dashboard') && !isBasicSurveyComplete ? styles.disabled : ''}`}
          onClick={(e) => handleTabClick(tab, e)}
        >
          <div className={styles.tabIcon}>{tab.icon}</div>
          <span className={styles.tabLabel}>{tab.label}</span>
        </Link>
      ))}
    </nav>
  );
}; 