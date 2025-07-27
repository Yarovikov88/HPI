import React, { useState, useEffect, useMemo } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { SPHERES } from '../data/spheres';
import { useSurvey } from '../hooks/useSurvey';
import styles from './Sidebar.module.css';

interface NavItem {
  path: string;
  text: string;
  id: string;
  isComplete?: boolean;
}

const STEP_NAMES = ['Проблемы', 'Цели', 'Блокеры', 'Метрики', 'Достижения'];

const Sidebar: React.FC = () => {
  const { user } = useAuth();
  const { isSphereComplete, isProStepComplete, groupedQuestions } = useSurvey();
  const location = useLocation();
  const navigate = useNavigate();
  const [isDiagnosticsOpen, setDiagnosticsOpen] = useState(false);
  const [isDashboardsOpen, setDashboardsOpen] = useState(false);
  const [isHistoryOpen, setHistoryOpen] = useState(false);
  const [isBasicOpen, setBasicOpen] = useState(false);
  const [isProOpen, setProOpen] = useState(false);

  useEffect(() => {
    const isDiagnosticsPage = location.pathname.startsWith('/account/diagnostics') || location.pathname.startsWith('/survey') || location.pathname.startsWith('/pro-survey');
    const isDashboardsPage = location.pathname.startsWith('/account');

    if (isDiagnosticsPage) {
      setDiagnosticsOpen(true);
    }
    if (isDashboardsPage) {
        setDashboardsOpen(true)
    }

    setBasicOpen(location.pathname.startsWith('/survey'));
    setProOpen(location.pathname.startsWith('/pro-survey'));
  }, [location.pathname]);

  const sphereOrder = Object.keys(SPHERES);
  const sphereIds = useMemo(() => Object.keys(groupedQuestions).sort((a, b) => sphereOrder.indexOf(a) - sphereOrder.indexOf(b)), [groupedQuestions, sphereOrder]);

  const basicSurveyChildren: NavItem[] = sphereIds.map(sphereId => {
      const sphereData = SPHERES[sphereId];
      const sphereText = sphereData ? sphereData.name : sphereId;
      const isComplete = isSphereComplete(sphereId);
      
      return { 
        path: `/survey?sphere=${sphereId}`, 
        text: sphereText, 
        id: sphereId,
        isComplete: isComplete,
      };
  });

  const isBasicSurveyFullyComplete = useMemo(() => {
    if (sphereIds.length === 0) return false;
    return sphereIds.every(sphereId => isSphereComplete(sphereId));
  }, [sphereIds, isSphereComplete]);

  const proSurveyChildren: NavItem[] = STEP_NAMES.map((name: string, index: number) => {
    const isComplete = isProStepComplete(index);
    return {
      path: `/pro-survey?step=${index}`,
      text: `${name}`,
      id: `${index}`,
      isComplete: isComplete,
    }
  });

  const isProSurveyFullyComplete = useMemo(() => {
    if (proSurveyChildren.length === 0) return false;
    return proSurveyChildren.every(child => child.isComplete);
  }, [proSurveyChildren]);

  const currentSearch = new URLSearchParams(location.search);
  const currentSphere = currentSearch.get('sphere');
  const currentStep = currentSearch.get('step');
  
  return (
    <aside className={styles.sidebar}>
      <div className={styles.userInfo}>
        <h4>{user?.full_name || 'Гость'}</h4>
        <p>{user?.email}</p>
      </div>
      <nav className={styles.nav}>
        <div className={styles.collapsibleSection}>
          <a
            href="#"
            onClick={(e) => { e.preventDefault(); setDashboardsOpen(!isDashboardsOpen); }}
            className={`${styles.navLink} ${styles.collapsibleTrigger} ${isDashboardsOpen ? styles.active : ''}`}
          >
            <span>Дашборды</span>
            <span className={`${styles.chevron} ${isDashboardsOpen ? styles.open : ''}`}></span>
          </a>
          {isDashboardsOpen && (
            <div className={styles.collapsibleContent}>
              <NavLink to="/account/dashboard" end className={({ isActive }) => `${styles.childLink} ${isActive ? styles.activeChild : ''}`}>
                <span>Базовый</span>
                {isBasicSurveyFullyComplete ? <span className={styles.checkMark}>✅</span> : <span className={styles.checkMark}>❔</span>}
              </NavLink>
              <NavLink to="/account/pro-dashboard" className={({ isActive }) => `${styles.childLink} ${isActive ? styles.activeChild : ''}`}>
                <span>Pro</span>
                {isProSurveyFullyComplete ? <span className={styles.checkMark}>✅</span> : <span className={styles.checkMark}>❔</span>}
              </NavLink>
            </div>
          )}
        </div>

        <div className={styles.collapsibleSection}>
          <a
            href="/account/diagnostics"
            onClick={(e) => {
              e.preventDefault();
              navigate('/account/diagnostics');
              setDiagnosticsOpen(!isDiagnosticsOpen);
            }}
            className={`${styles.navLink} ${styles.collapsibleTrigger} ${isDiagnosticsOpen ? styles.active : ''}`}
          >
            <span>Диагностика</span>
            <span className={`${styles.chevron} ${isDiagnosticsOpen ? styles.open : ''}`}></span>
          </a>
          {isDiagnosticsOpen && (
            <div className={styles.collapsibleContent}>
              <a href='#' onClick={(e) => {e.preventDefault(); setBasicOpen(!isBasicOpen)}} className={`${styles.childLink} ${styles.collapsibleTrigger}`}>
                <span style={{ display: 'flex', alignItems: 'center' }}>
                  <span>Базовая</span>
                  {isBasicSurveyFullyComplete ? <span className={styles.checkMark}>✅</span> : <span className={styles.checkMark}>❔</span>}
                </span>
                <span className={`${styles.chevron} ${isBasicOpen ? styles.open : ''}`}></span>
              </a>
              {isBasicOpen && (
                <div className={styles.subSubMenu}>
                    {basicSurveyChildren.map(child => {
                      const isActive = child.id === currentSphere;
                      return (
                        <NavLink key={child.path} to={child.path} className={isActive ? styles.activeChild : styles.childLink}>
                          <span>{child.text}</span>
                          {child.isComplete && <span className={styles.checkMark}>✅</span>}
                        </NavLink>
                      )
                    })}
                  </div>
                )}
              
              <a href='#' onClick={(e) => {e.preventDefault(); setProOpen(!isProOpen)}} className={`${styles.childLink} ${styles.collapsibleTrigger}`}>
                <span style={{ display: 'flex', alignItems: 'center' }}>
                  <span>Pro</span>
                  {isProSurveyFullyComplete ? <span className={styles.checkMark}>✅</span> : <span className={styles.checkMark}>❔</span>}
                </span>
                <span className={`${styles.chevron} ${isProOpen ? styles.open : ''}`}></span>
              </a>
              {isProOpen && (
                  <div className={styles.subSubMenu}>
                    {proSurveyChildren.map(child => {
                      const isActive = child.id === currentStep;
                      return (
                        <NavLink key={child.path} to={child.path} className={isActive ? styles.activeChild : styles.childLink}>
                          <span>{child.text}</span>
                          {child.isComplete && <span className={styles.checkMark}>✅</span>}
                        </NavLink>
                      )
                    })}
                  </div>
                )}
            </div>
          )}
        </div>

        <div className={styles.collapsibleSection}>
          <a
            href="#"
            onClick={(e) => { e.preventDefault(); setHistoryOpen(!isHistoryOpen); }}
            className={`${styles.navLink} ${styles.collapsibleTrigger}`}
          >
            <span>История</span>
            <span className={`${styles.chevron} ${isHistoryOpen ? styles.open : ''}`}></span>
          </a>
          {isHistoryOpen && (
            <div className={styles.collapsibleContent}>
              {/* Coming soon */}
            </div>
          )}
        </div>
      </nav>
    </aside>
  );
};

export default Sidebar; 