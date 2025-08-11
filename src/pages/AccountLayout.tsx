import React, { useEffect, useRef, useState } from 'react';
import { NavLink, useLocation, Outlet, useNavigate } from 'react-router-dom';
import styles from './AccountLayout.module.css';
import { useAuth } from '../hooks/useAuth';
import { useSurvey } from '../hooks/useSurvey';
import { CalendarWidget } from '../components/CalendarWidget';
import { SPHERE_ORDERED } from '../data/spheres';
import { proSections } from '../data/proSections';

const AccountLayout: React.FC = () => {
  const { user } = useAuth();
  const surveyData = useSurvey(); // Сначала получаем весь объект
  const location = useLocation();
  const navigate = useNavigate();
  const searchParams = new URLSearchParams(location.search);
  const currentSphereId = searchParams.get('sphere');
  const dateParam = searchParams.get('date');
  const dateSuffix = dateParam ? `?date=${dateParam}` : '';

  // Управляем сворачиванием/разворачиванием секций
  const [isDiagnosticsOpen, setDiagnosticsOpen] = useState<boolean>(true);
  const [isBasicOpen, setBasicOpen] = useState<boolean>(location.pathname.includes('/survey'));
  const [isProOpen, setProOpen] = useState<boolean>(location.pathname.includes('/pro/'));
  const basicRef = useRef<HTMLDetailsElement | null>(null);
  const proRef = useRef<HTMLDetailsElement | null>(null);
  const diagnosticsRef = useRef<HTMLDetailsElement | null>(null);

  // Синхронизация с маршрутом
  useEffect(() => {
    if (location.pathname.includes('/diagnostics')) {
      // На странице диагностик не трогаем состояние верхнего блока -> пользователь сам сворачивает/разворачивает
      setBasicOpen(false);
      setProOpen(false);
      if (basicRef.current) basicRef.current.open = false;
      if (proRef.current) proRef.current.open = false;
      return;
    }
    // На внутренних маршрутах раздела держим верхний блок открытым
    const onInner = location.pathname.includes('/survey') || location.pathname.includes('/pro/');
    setDiagnosticsOpen(onInner ? true : isDiagnosticsOpen);
    setBasicOpen(location.pathname.includes('/survey'));
    setProOpen(location.pathname.includes('/pro/'));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname]);

  // Если данные еще не загружены, показываем заглушку
  if (!surveyData) {
    return <div>Загрузка данных опроса...</div>;
  }

  // Теперь мы можем безопасно деструктурировать
  const { 
    isBasicSurveyComplete, 
    isProSurveyComplete, 
    isSphereComplete, 
    isProCategoryComplete 
  } = surveyData;

  const isDashboardsActive = location.pathname.includes('/dashboard') || location.pathname.includes('/pro-dashboard');

  return (
    <div className={styles.accountLayout}>
      <aside className={styles.sidebar}>
        <nav className={styles.nav}>
          <ul>
            <li>
              <details ref={diagnosticsRef} open={isDiagnosticsOpen} onToggle={(e) => setDiagnosticsOpen((e.currentTarget as HTMLDetailsElement).open)}>
                <summary
                  className={styles.sectionTitle}
                  onClick={() => {
                    // Навигация на diagnostics; верхний блок будет toggled нативно
                    navigate('/account/diagnostics' + dateSuffix);
                    // Сворачиваем вложенные секции
                    setBasicOpen(false);
                    setProOpen(false);
                    if (basicRef.current) basicRef.current.open = false;
                    if (proRef.current) proRef.current.open = false;
                  }}
                >
                  Диагностика
                </summary>
                <ul className={styles.submenu}>
                  <li>
                    <details ref={basicRef} open={isBasicOpen} onToggle={(e) => setBasicOpen((e.currentTarget as HTMLDetailsElement).open)}>
                      <summary>Базовая {isBasicSurveyComplete && <span className={styles.check}>✔</span>}</summary>
                      <ul className={styles.submenu}>
                        {SPHERE_ORDERED.map(sphere => (
                          <li key={sphere.id}>
                            <NavLink to={`/account/survey?sphere=${sphere.id}${dateParam ? `&date=${dateParam}` : ''}`}>
                              {sphere.name} {isSphereComplete(sphere.id) && <span className={styles.check}>✔</span>}
                            </NavLink>
                          </li>
                        ))}
                      </ul>
                    </details>
                  </li>
                  <li>
                    <details ref={proRef} open={isProOpen} onToggle={(e) => setProOpen((e.currentTarget as HTMLDetailsElement).open)}>
                      <summary>Pro {isProSurveyComplete && <span className={styles.check}>✔</span>}</summary>
                      <ul className={styles.submenu}>
                        {proSections.map(section => (
                          <li key={section.category}>
                            <NavLink to={`/account/pro/${section.category}${dateParam ? `?date=${dateParam}` : ''}`}>
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
                    <NavLink to={`/account/dashboard${dateSuffix}`} end>
                      Базовый
                    </NavLink>
                  </li>
                  <li>
                    <NavLink to={`/account/pro-dashboard${dateSuffix}`}>
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
      <div className={styles.activeUserBadge}>
        ID пользователя: {user?.id ?? '—'}
      </div>
    </div>
  );
};

export default AccountLayout; 