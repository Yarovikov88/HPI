import React, { useState, useEffect, useMemo, useContext } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { SPHERES, SPHERE_ORDERED } from '../data/spheres';
import { useSurvey } from '../hooks/useSurvey';
import styles from './Sidebar.module.css';
import { proSections } from '../data/proSections';

interface NavItem {
  path: string;
  text: string;
  id: string;
  isComplete?: boolean;
}

const STEP_NAMES = ['Проблемы', 'Цели', 'Блокеры', 'Метрики', 'Достижения'];

const Sidebar: React.FC = () => {
  console.log('🔄 Sidebar: компонент рендерится');
  
  const { user } = useAuth();
  const surveyContext = useSurvey();
  
  console.log('🔄 Sidebar: useSurvey() вернул:', surveyContext);
  console.log('🔄 Sidebar: proAnswers из useSurvey:', surveyContext?.proAnswers);
  console.log('🔄 Sidebar: proCompletionStatus из useSurvey:', surveyContext?.proCompletionStatus);
  
  if (!surveyContext) {
    console.error('❌ Sidebar: SurveyContext не найден!');
    return null;
  }
  
  const { 
    basicQuestions, 
    groupedQuestions, 
    answers, 
    proAnswers, 
    groupedProQuestions, 
    proSections,
    isSphereComplete,
    isBasicSurveyComplete,
    isProSurveyComplete,
    proCompletionStatus
  } = surveyContext;
  
  console.log('🔄 Sidebar: proAnswers:', proAnswers);
  console.log('🔄 Sidebar: groupedProQuestions:', groupedProQuestions);
  console.log('🔄 Sidebar: proCompletionStatus после деструктуризации:', proCompletionStatus);
  console.log('🔄 Sidebar: SPHERE_ORDERED:', SPHERE_ORDERED);
  const location = useLocation();
  const navigate = useNavigate();
  const [isDiagnosticsOpen, setDiagnosticsOpen] = useState(false);
  const [isDashboardsOpen, setDashboardsOpen] = useState(false);
  const [isHistoryOpen, setHistoryOpen] = useState(false);
  const [isBasicOpen, setBasicOpen] = useState(false);
  const [isProOpen, setProOpen] = useState(false);
  const [forceUpdate, setForceUpdate] = useState(0);

  // Подписываемся на изменения proAnswers для принудительного перерендера
  useEffect(() => {
    console.log('🔄 Sidebar: useEffect для proAnswers сработал');
    console.log('🔄 Sidebar: proAnswers изменился, принудительно перерендериваемся');
    console.log('🔄 Sidebar: proAnswers:', proAnswers);
    
    // Принудительно перерендериваем компонент
    setForceUpdate((prev: number) => prev + 1);
  }, [proAnswers]);

  const sphereOrder = Object.keys(SPHERES);
  const sphereIds = useMemo(
    () => Object.keys(groupedQuestions).sort((a, b) => sphereOrder.indexOf(a) - sphereOrder.indexOf(b)),
    [groupedQuestions, sphereOrder]
  );

  const basicSurveyChildren: NavItem[] = sphereIds.map((sphereId: string) => {
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

  // Используем флаги из контекста — они же показываются в «Диагностика»
  const isBasicSurveyFullyComplete = isBasicSurveyComplete;
  const isProSurveyFullyComplete = isProSurveyComplete;

  // Fail-safe: дублируем вычисление локально и объединяем через OR,
  // чтобы бейджи в «Дашборды» точно совпадали с «Диагностика»
  const isBasicCompleteFailSafe = useMemo(() => {
    if (isBasicSurveyFullyComplete) return true;
    if (sphereIds.length === 0) return false;
    return sphereIds.every((sphereId: string) => isSphereComplete(sphereId));
  }, [isBasicSurveyFullyComplete, sphereIds, isSphereComplete]);

  const isProCompleteFailSafe = useMemo(() => {
    if (isProSurveyFullyComplete) return true;
    
    // Используем статус из backend если доступен
    if (proCompletionStatus) {
      console.log('🔍 Sidebar: Используем статус завершения из backend:', proCompletionStatus);
      return proCompletionStatus.overall_complete;
    }
    
    console.log('🔍 Sidebar: Backend статус недоступен, используем локальную логику...');
    console.log('🔍 Sidebar: proAnswers:', proAnswers);
    console.log('🔍 Sidebar: groupedProQuestions:', groupedProQuestions);
    
    // Проверяем, завершены ли все PRO категории для всех сфер (помесячно по сферам)
    const result = SPHERE_ORDERED.every((sphere) => {
      console.log(`📊 Sidebar: Проверяем сферу ${sphere.id} (${sphere.name})`);
      
      return proSections.every((section: any) => {
        const questionsForCategory = groupedProQuestions[section.category] || [];
        const sphereQuestions = questionsForCategory.filter((q: any) => q.sphere_id === sphere.id || q.sphere_api_id === Number(sphere.id || 0));
        
        console.log(`📊 Sidebar: Категория ${section.category}, вопросов для сферы ${sphere.id}: ${sphereQuestions.length}`);
        
        // Если для категории нет вопросов для этой сферы, считаем категорию завершенной (нет данных — нет требований)
        if (sphereQuestions.length === 0) {
          console.log(`📊 Sidebar: Категория ${section.category} для сферы ${sphere.id} - нет вопросов, считаем завершенной`);
          return true;
        }
        
        const categoryComplete = sphereQuestions.every((q: any) => {
          const keyByName = `${section.category}-${q.sphere_id}`;
          const keyByNum = `${section.category}-${String(q.sphere_api_id ?? '')}`;
          const ans = proAnswers[keyByName] || proAnswers[keyByNum];
          
          console.log(`📊 Sidebar: Вопрос ${q.id}, ключи: ${keyByName}, ${keyByNum}, ответ:`, ans);
          
          const hasAnswer = !!(ans && typeof ans.text === 'string' && ans.text.trim().length > 0);
          console.log(`📊 Sidebar: Вопрос ${q.id} имеет ответ: ${hasAnswer}`);
          
          return hasAnswer;
        });
        
        console.log(`📊 Sidebar: Категория ${section.category} для сферы ${sphere.id} завершена: ${categoryComplete}`);
        return categoryComplete;
      });
    });
    
    console.log('🔍 Sidebar: Итоговый результат PRO завершенности:', result);
    return result;
  }, [isProSurveyFullyComplete, proCompletionStatus, proAnswers, groupedProQuestions, proSections]);

  // Создаем PRO элементы для каждой сферы жизни
  const proSurveyChildren: NavItem[] = useMemo(() => {
    console.log('🔍 Sidebar: useMemo proSurveyChildren ВЫЗВАН!');
    console.log('🔍 Sidebar: Создаем PRO элементы для каждой сферы жизни');
    console.log('🔍 Sidebar: proCompletionStatus:', proCompletionStatus);
    console.log('🔍 Sidebar: proAnswers keys:', Object.keys(proAnswers));
    console.log('🔍 Sidebar: SPHERE_ORDERED length:', SPHERE_ORDERED.length);
    
    if (proCompletionStatus && proCompletionStatus.spheres) {
      console.log('🔍 Sidebar: Доступные сферы в статусе:', Object.keys(proCompletionStatus.spheres));
    }
    
    const result = SPHERE_ORDERED.map((sphere) => {
      console.log(`🔍 Sidebar: Обрабатываем сферу ${sphere.name} (${sphere.id})`);
      let isSphereProComplete = false;
      
      // Используем статус из backend если доступен
      if (proCompletionStatus && proCompletionStatus.spheres) {
        const sphereKey = `sphere_${sphere.id}`;
        const sphereData = proCompletionStatus.spheres[sphereKey];
        console.log(`🔍 Sidebar: Сфера ${sphere.name} (${sphere.id}), sphereKey: ${sphereKey}, данные:`, sphereData);
        
        if (sphereData) {
          isSphereProComplete = sphereData.is_complete;
          console.log(`🔍 Sidebar: Сфера ${sphere.name} завершена: ${isSphereProComplete}`);
        } else {
          console.log(`🔍 Sidebar: Нет данных для сферы ${sphere.name} с ключом ${sphereKey}`);
        }
      } else {
        console.log('🔍 Sidebar: proCompletionStatus.spheres недоступен, используем fallback');
      }
      
      // Fallback: локальная логика если backend статус недоступен
      if (!proCompletionStatus) {
        console.log('🔍 Sidebar: Backend статус недоступен, используем локальную логику...');
        
        // Проверяем, завершены ли все PRO категории для данной сферы
        isSphereProComplete = proSections.every((section: any) => {
          const questionsForCategory = groupedProQuestions[section.category] || [];
          const sphereQuestions = questionsForCategory.filter((q: any) => q.sphere_id === sphere.id || q.sphere_api_id === Number(sphere.id || 0));
          
          console.log(`🔍 Sidebar: Сфера ${sphere.name}, категория ${section.category}, вопросов: ${sphereQuestions.length}`);
          
          if (sphereQuestions.length === 0) return true;
          
          const categoryComplete = sphereQuestions.every((q: any) => {
            // Используем те же ключи, что и в SurveyContext
            const keyByString = `${section.category}-${sphere.id}`;
            const keyByNumeric = `${section.category}-${String(sphere.id || '')}`;
            const ans = proAnswers[keyByString] || proAnswers[keyByNumeric];
            
            console.log(`🔍 Sidebar: Вопрос ${q.id}, ключи: ${keyByString}, ${keyByNumeric}, ответ:`, ans);
            
            const hasAnswer = !!(ans && typeof ans.text === 'string' && ans.text.trim().length > 0);
            console.log(`🔍 Sidebar: Вопрос ${q.id} имеет ответ: ${hasAnswer}`);
            
            return hasAnswer;
          });
          
          console.log(`🔍 Sidebar: Категория ${section.category} для сферы ${sphere.name} завершена: ${categoryComplete}`);
          return categoryComplete;
        });
      }

      console.log(`📊 Сфера "${sphere.name}" (${sphere.id}) завершена: ${isSphereProComplete}`);
      
      return {
        id: `pro-${sphere.id}`,
        label: sphere.name,
        path: `/account/pro/sphere/${sphere.id}`,
        icon: sphere.emoji,
        isComplete: isSphereProComplete,
        isPro: true
      };
    });
    
    console.log('🔄 Sidebar: Результат proSurveyChildren:', result);
    return result;
  }, [proCompletionStatus, proAnswers, groupedProQuestions, proSections, SPHERE_ORDERED]);

  // Отладочная информация для понимания состояния
  console.log('=== SIDEBAR DEBUG ===');
  console.log('SPHERE_ORDERED:', SPHERE_ORDERED);
  console.log('groupedProQuestions:', groupedProQuestions);
  console.log('proAnswers:', proAnswers);
  console.log('proSections:', proSections);
  console.log('proSurveyChildren:', proSurveyChildren);
  
  // Дополнительная отладочная информация для PRO ответов
  console.log('🔍 PRO ответы по категориям:');
  proSections.forEach((section: any) => {
    const answersForCategory = Object.keys(proAnswers).filter(k => k.startsWith(section.category));
    console.log(`  ${section.name} (${section.category}):`, answersForCategory.length, 'ответов');
    answersForCategory.forEach(key => {
      const answer = proAnswers[key];
      console.log(`    ${key}:`, answer?.text?.substring(0, 50) || 'пустой');
    });
  });

  const currentSearch = new URLSearchParams(location.search);
  const currentSphere = currentSearch.get('sphere');
  const currentStep = currentSearch.get('step');
  // Получаем sphereId из URL для PRO страниц
  const currentSphereId = location.pathname.split('/').pop();

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
            onClick={(e: React.MouseEvent) => {
              e.preventDefault();
              setDashboardsOpen(!isDashboardsOpen);
            }}
            className={`${styles.navLink} ${styles.collapsibleTrigger} ${isDashboardsOpen ? styles.active : ''}`}
          >
            <span>Дашборды</span>
            <span className={`${styles.chevron} ${isDashboardsOpen ? styles.open : ''}`}></span>
          </a>
          {isDashboardsOpen && (
            <div className={styles.collapsibleContent}>
              <NavLink 
                to="/account/dashboard" 
                end 
                className={({ isActive }: { isActive: boolean }) => `${styles.childLink} ${isActive ? styles.activeChild : ''} ${!isBasicCompleteFailSafe ? styles.disabled : ''}`}
                onClick={(e: React.MouseEvent) => {
                  if (!isBasicCompleteFailSafe) {
                    e.preventDefault();
                    alert('Для доступа к дашборду необходимо завершить базовую диагностику.');
                    return;
                  }
                }}
              >
                <span>Базовый</span>
                {isBasicCompleteFailSafe ? (
                  <span className={styles.checkMark}>✅</span>
                ) : (
                  <span className={styles.checkMark}>❔</span>
                )}
              </NavLink>
              <NavLink 
                to="/account/pro-dashboard" 
                className={({ isActive }: { isActive: boolean }) => `${styles.childLink} ${isActive ? styles.activeChild : ''} ${!isProCompleteFailSafe ? styles.disabled : ''}`}
                onClick={(e: React.MouseEvent) => {
                  if (!isProCompleteFailSafe) {
                    e.preventDefault();
                    alert('Для доступа к PRO дашборду необходимо завершить PRO диагностику.');
                    return;
                  }
                }}
              >
                <span>Pro</span>
                {isProCompleteFailSafe ? (
                  <span className={styles.checkMark}>✅</span>
                ) : (
                  <span className={styles.checkMark}>❔</span>
                )}
              </NavLink>
            </div>
          )}
        </div>

        <div className={styles.collapsibleSection}>
          <a
            href="/account/diagnostics"
            onClick={(e: React.MouseEvent) => {
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
              <a
                href="#"
                onClick={(e: React.MouseEvent) => {
                  e.preventDefault();
                  setBasicOpen(!isBasicOpen);
                }}
                className={`${styles.childLink} ${styles.collapsibleTrigger}`}
              >
                <span style={{ display: 'flex', alignItems: 'center' }}>
                  <span>Базовая</span>
                  {isBasicSurveyFullyComplete ? (
                    <span className={styles.checkMark}>✅</span>
                  ) : (
                    <span className={styles.checkMark}>❔</span>
                  )}
                </span>
                <span className={`${styles.chevron} ${isBasicOpen ? styles.open : ''}`}></span>
              </a>
              {isBasicOpen && (
                <div className={styles.subSubMenu}>
                  {basicSurveyChildren.map((child) => {
                    const isActive = child.id === currentSphere;
                    return (
                      <NavLink key={child.path} to={child.path} className={isActive ? styles.activeChild : styles.childLink}>
                        <span>{child.text}</span>
                        {child.isComplete && <span className={styles.checkMark}>✅</span>}
                      </NavLink>
                    );
                  })}
                </div>
              )}

              <a
                href="#"
                onClick={(e: React.MouseEvent) => {
                  e.preventDefault();
                  setProOpen(!isProOpen);
                }}
                className={`${styles.childLink} ${styles.collapsibleTrigger}`}
              >
                <span style={{ display: 'flex', alignItems: 'center' }}>
                  <span>Pro</span>
                  {isProSurveyFullyComplete ? (
                    <span className={styles.checkMark}>✅</span>
                  ) : (
                    <span className={styles.checkMark}>❔</span>
                  )}
                </span>
                <span className={`${styles.chevron} ${isProOpen ? styles.open : ''}`}></span>
              </a>
              {isProOpen && (
                <div className={styles.subSubMenu}>
                  {proSurveyChildren.map((child) => {
                    const isActive = child.id === currentSphereId;
                    return (
                      <NavLink key={child.path} to={child.path} className={isActive ? styles.activeChild : styles.childLink}>
                        <span>{child.text}</span>
                        {child.isComplete && <span className={styles.checkMark}>✅</span>}
                      </NavLink>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>

        <div className={styles.collapsibleSection}>
          <a
            href="#"
            onClick={(e: React.MouseEvent) => {
              e.preventDefault();
              setHistoryOpen(!isHistoryOpen);
            }}
            className={`${styles.navLink} ${styles.collapsibleTrigger}`}
          >
            <span>История</span>
            <span className={`${styles.chevron} ${isHistoryOpen ? styles.open : ''}`}></span>
          </a>
          {isHistoryOpen && (
            <div className={styles.collapsibleContent}>
              <NavLink to="/account/history" className={({ isActive }: { isActive: boolean }) => `${styles.childLink} ${isActive ? styles.activeChild : ''}`}>
                <span>История ответов</span>
              </NavLink>
            </div>
          )}
        </div>
      </nav>
    </aside>
  );
};

export default Sidebar; 