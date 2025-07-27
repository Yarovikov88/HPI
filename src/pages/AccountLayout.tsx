import React from 'react';
import { NavLink, useLocation, Outlet } from 'react-router-dom';
import styles from './AccountLayout.module.css';
import { useAuth } from '../hooks/useAuth';
import { useSurvey } from '../hooks/useSurvey';
import { CalendarWidget } from '../components/CalendarWidget';
import { SPHERE_ORDERED } from '../data/spheres';
import { proSections } from '../data/proSections';

const AccountLayout: React.FC = () => {
  const { user } = useAuth();
  const { 
    isBasicSurveyComplete, 
    isProSurveyComplete, 
    isSphereComplete, 
    isProCategoryComplete 
  } = useSurvey();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const currentSphereId = searchParams.get('sphere');

  const isDiagnosticsActive = location.pathname.includes('/diagnostics') || location.pathname.includes('/survey') || location.pathname.includes('/pro/');
  const isDashboardsActive = location.pathname.includes('/dashboard') || location.pathname.includes('/pro-dashboard');

  return (
    <div className={styles.accountLayout}>
      <aside className={styles.sidebar}>
        <nav className={styles.nav}>
          <ul>
            <li>
              <details open={isDiagnosticsActive}>
                <summary className={styles.sectionTitle}>Диагностика</summary>
                <ul className={styles.submenu}>
                  <li>
                    <details open={location.pathname.includes('/survey')}>
                      <summary>Базовая {isBasicSurveyComplete && <span className={styles.check}>✔</span>}</summary>
                      <ul className={styles.submenu}>
                        {SPHERE_ORDERED.map(sphere => (
                          <li key={sphere.id}>
                            <NavLink to={`/account/survey?sphere=${sphere.id}`}>
                              {sphere.name} {isSphereComplete(sphere.id) && <span className={styles.check}>✔</span>}
                            </NavLink>
                          </li>
                        ))}
                      </ul>
                    </details>
                  </li>
                  <li>
                    <details open={location.pathname.includes('/pro/')}>
                      <summary>Pro {isProSurveyComplete && <span className={styles.check}>✔</span>}</summary>
                      <ul className={styles.submenu}>
                        {proSections.map(section => (
                          <li key={section.category}>
                            <NavLink to={`/account/pro/${section.category}`}>
                              {section.name} {isProCategoryComplete(section.category) && <span className={styles.check}>✔</span>}
                            </NavLink>
                          </li>
                        ))}
                      </ul>
                    </details>
                  </li>
                </ul>
              </details>
            </li>
            <li>
              <details open={isDashboardsActive}>
                <summary className={styles.sectionTitle}>Дашборды</summary>
                <ul className={styles.submenu}>
                  <li>
                    <NavLink to="/account/dashboard" end>
                      Базовый
                    </NavLink>
                  </li>
                  <li>
                    <NavLink to="/account/pro-dashboard">
                      Pro
                    </NavLink>
                  </li>
                </ul>
              </details>
            </li>
            <li>
              <details open>
                <summary className={styles.sectionTitle}>История</summary>
                <CalendarWidget />
              </details>
            </li>
          </ul>
        </nav>
      </aside>
      <main className={styles.mainContent}>
        <Outlet />
      </main>
    </div>
  );
};

export default AccountLayout; 