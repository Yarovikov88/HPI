import React, { useMemo, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import styles from './DiagnosticsPage.module.css';
import { useSurvey } from '../hooks/useSurvey';

export default function DiagnosticsPage() {
  const navigate = useNavigate();
  const location = useLocation();
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
    proCtaLabel = 'Сначала пройдите обычную';
    proCtaDisabled = true;
  } else if (isBasicDraft && !isBasicDone) {
    proCtaLabel = 'Сначала завершите обычную';
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

  return (
      <div>
        <div className={styles.titleRow}>
          <h2 className={styles.title}>Диагностика</h2>
          <div className={styles.dateBadge}>{displayDate}</div>
        </div>
        <p>Выберите опросник, который хотите пройти, чтобы оценить свой потенциал.</p>
        <div className={styles.diagnosticsContainer}>
          <div className={styles.surveyCard}>
            <h3>Базовая диагностика</h3>
            <p>Оцените свое состояние по 8 ключевым сферам жизни. Это займет не более 5 минут.</p>
            <button
              onClick={basicCtaAction}
              className={basicCtaLabel === 'Посмотреть ответы' ? styles.secondaryButton : styles.ctaButton}
            >
              {basicCtaLabel}
            </button>
          </div>
          <div className={styles.surveyCard}>
            <h3>Pro диагностика</h3>
            <p>Комплексная оценка по профессиональным методикам. Чтобы получить индивидуальные рекомендации с глубокой проработкой от AI, необходимо пройти Pro диагностику.</p>
            <button
              onClick={proCtaAction}
              disabled={proCtaDisabled}
              className={proCtaLabel === 'Посмотреть ответы' ? styles.secondaryButton : styles.ctaButton}
            >
              {proCtaLabel}
            </button>
          </div>
        </div>
      </div>
  );
} 