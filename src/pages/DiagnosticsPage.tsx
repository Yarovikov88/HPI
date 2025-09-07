import React, { useMemo, useEffect, useState } from 'react';
import { useNavigate, useLocation, NavLink } from 'react-router-dom';
import styles from './DiagnosticsPage.module.css';
import { useSurvey } from '../hooks/useSurvey';
import { ProBasicHeader } from '../components/ProBasicHeader';

export default function DiagnosticsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { state } = location;
  const [notification, setNotification] = useState(state?.message || null);
  const { isDataReady } = useSurvey();

  useEffect(() => {
    // Если мы перешли на эту страницу с сообщением,
    // и пользователь начинает взаимодействовать со страницей (например, переходит на другую дату),
    // мы убираем уведомление, чтобы оно не висело постоянно.
    if (notification) {
      // Очищаем state, чтобы уведомление не появилось снова при возврате на эту страницу
      window.history.replaceState({}, document.title)
    }
  }, [location.pathname, location.search]);

  const {
    getBasicSurveyProgress,
    isBasicSurveyComplete,
    getProSurveyProgress,
    isProSurveyComplete,
    setSelectedDate,
  } = useSurvey();

  const basic = useMemo(() => getBasicSurveyProgress(), [getBasicSurveyProgress]);
  const pro = useMemo(() => getProSurveyProgress(), [getProSurveyProgress]);

  // Выбранная дата из ?date=YYYY-MM-DD
  const searchParams = new URLSearchParams(location.search);
  const dateParam = searchParams.get('date');
  const dateSuffix = dateParam ? `?date=${dateParam}` : '';
  // Используем ЛОКАЛЬНУЮ дату (а не UTC), чтобы корректно определять «сегодня»
  const getLocalYMD = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  const todayStr = getLocalYMD(new Date());
  const isToday = !dateParam || dateParam === todayStr;
  const displayDate = dateParam ? new Date(dateParam).toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric' }) : new Date().toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric' });

  useEffect(() => {
    if (dateParam) {
      const parsed = new Date(dateParam);
      if (!Number.isNaN(parsed.getTime())) {
        setSelectedDate(parsed);
      }
    }
  }, [dateParam, setSelectedDate]);

  const isBasicEmpty = basic.total > 0 ? basic.answered === 0 : true;
  const isBasicDraft = basic.answered > 0 && basic.answered < basic.total;
  const isBasicDone = isBasicSurveyComplete;

  const isProEmpty = pro.total > 0 ? pro.answered === 0 : true;
  const isProDraft = pro.answered > 0 && pro.answered < pro.total;
  const isProDone = isProSurveyComplete;

  // Текст и действия для базовой
  let basicCtaLabel = 'Начать';
  let basicCtaAction = () => navigate('/account/survey' + dateSuffix);
  if (!isToday) {
    basicCtaLabel = 'Посмотреть ответы';
    basicCtaAction = () => navigate('/account/survey' + dateSuffix);
  } else if (isBasicDone && !isProDone && isProEmpty) {
    basicCtaLabel = 'Посмотреть ответы';
    basicCtaAction = () => navigate('/account/survey' + dateSuffix);
  } else if (isBasicDraft) {
    basicCtaLabel = 'Продолжить';
    basicCtaAction = () => navigate('/account/survey' + dateSuffix);
  } else if (isBasicDone && isProDone) {
    basicCtaLabel = 'Посмотреть ответы';
    basicCtaAction = () => navigate('/account/survey' + dateSuffix);
  }

  // Текст и действия для PRO
  let proCtaLabel = 'Начать';
  let proCtaDisabled = false;
  let proCtaAction: () => void = () => navigate('/account/pro/problems' + dateSuffix);

  if (!isToday) {
    proCtaLabel = 'Посмотреть ответы';
    proCtaDisabled = false;
    proCtaAction = () => navigate('/account/pro/problems' + dateSuffix);
  } else if (isBasicEmpty) {
    proCtaLabel = 'Сначала пройдите базовую';
    proCtaDisabled = true;
  } else if (isBasicDraft && !isBasicDone) {
    proCtaLabel = 'Сначала завершите базовую';
    proCtaDisabled = true;
  } else if (isProDraft) {
    proCtaLabel = 'Продолжить';
    proCtaAction = () => navigate('/account/pro/problems' + dateSuffix);
  } else if (isProDone) {
    proCtaLabel = 'Посмотреть ответы';
    proCtaAction = () => navigate('/account/pro/problems' + dateSuffix);
  } else if (isBasicDone && isProEmpty) {
    proCtaLabel = 'Начать';
    proCtaAction = () => navigate('/account/pro/problems' + dateSuffix);
  }

  const btnClassFor = (label: string) => {
    if (label === 'Начать') return styles.startBtn;
    if (label === 'Продолжить') return styles.continueBtn;
    if (label === 'Посмотреть ответы') return styles.viewBtn;
    return styles.startBtn;
  };

  const basicBtnClass = btnClassFor(basicCtaLabel);
  const proBtnClass = btnClassFor(proCtaLabel);

  // Add a disabled class when the button should be inactive
  const proBtnClasses = `${styles.ctaButton} ${proBtnClass} ${proCtaDisabled ? styles.disabledButton : ''}`;

  if (!isDataReady) {
    return (
      <div className={styles.pageWrapper}>
        <ProBasicHeader variant="diagnostics" dateText={displayDate} />
        <div className={styles.loading}>Загрузка…</div>
      </div>
    );
  }
  return (
      <div className={styles.diagnosticsPageWrapper}>
        <ProBasicHeader variant="diagnostics" dateText={displayDate} />
        {notification && (
          <div className={styles.notification}>
            <span>{notification}</span>
            <button onClick={() => setNotification(null)} className={styles.closeButton}>&times;</button>
          </div>
        )}
        <div className={styles.diagnosticsContainer}>
        {/* Убираем этот заголовок */}
        {/* <h1 className={styles.pageTitle}>Диагностика</h1> */}
          <div className={styles.surveyCard}>
            <h3>Базовая диагностика</h3>
            <p>Оцените свое состояние по 8 ключевым сферам жизни. Это займет не более 5 минут.</p>
            <NavLink to={`/account/survey${dateSuffix}`} className={`${styles.ctaButton} ${basicBtnClass}`}>
              {basicCtaLabel}
            </NavLink>
          </div>
          <div className={`${styles.surveyCard} ${styles.proCard}`}>
            <h3>Pro диагностика</h3>
            <p>Комплексная оценка по профессиональным методикам. Чтобы получить индивидуальные рекомендации с глубокой проработкой от AI, необходимо пройти Pro диагностику.</p>
            <NavLink
              to={proCtaDisabled ? '#' : `/account/pro/problems${dateSuffix}`}
              className={proBtnClasses}
            onClick={(e) => { if (proCtaDisabled) e.preventDefault(); }}
            >
              {proCtaLabel}
            </NavLink>
          </div>
        </div>
      </div>
  );
} 