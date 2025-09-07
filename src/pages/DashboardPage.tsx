import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import { apiClient } from '../services/api';
import type { Recommendation } from '../services/api';
import styles from './DashboardPage.module.css';
import { SPHERE_ORDERED } from '../data/spheres';
import { TrendChart } from '../components/TrendChart';
import { RadarChart } from '../components/RadarChart';
import { ProBasicHeader } from '../components/ProBasicHeader';
import { useSurvey } from '../hooks/useSurvey';

const parseYmd = (ymd: string): Date | null => {
  const parts = ymd.split('-');
  if (parts.length !== 3) return null;
  const year = parseInt(parts[0], 10);
  const month = parseInt(parts[1], 10) - 1; // Month is 0-indexed in JS Date
  const day = parseInt(parts[2], 10);
  if (isNaN(year) || isNaN(month) || isNaN(day)) return null;
  return new Date(year, month, day);
};

interface SphereTrendMiniProps {
  id: string;
  name: string;
  params: { month?: string; date?: string };
  radarValue?: number; // Добавляем значение из радара
}

// Генерируем прямую линию на основе значения из радара
const generateFlatLineData = (radarValue: number) => {
  const today = new Date();
  const dates: string[] = [];
  const scores: number[] = [];
  
  // Генерируем 7 дней
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    dates.push(date.toISOString().split('T')[0]);
    scores.push(radarValue);
  }
  
  return dates.map((date, index) => ({
    date,
    score: scores[index]
  }));
};

const SphereTrendMini: React.FC<SphereTrendMiniProps> = ({ id, name, params, radarValue }: SphereTrendMiniProps) => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<{ date: string; score: number }[]>([]);
  
  useEffect(() => {
    setLoading(true);
    apiClient.getSphereTrend(id, params.month, params.date)
      .then((r) => {
        const realData = (r?.trend ?? []) as any;
        if (realData && realData.length > 0) {
          setData(realData);
        } else if (radarValue) {
          // Если нет тренда, показываем прямую линию на уровне значения из радара
          setData(generateFlatLineData(radarValue));
        } else {
          setData([]);
        }
      })
      .catch(() => {
        if (radarValue) {
          // В случае ошибки показываем прямую линию на уровне значения из радара
          setData(generateFlatLineData(radarValue));
        } else {
          setData([]);
        }
      })
      .finally(() => setLoading(false));
  }, [id, JSON.stringify(params), radarValue]);
  
  return (
    <div style={{ border: '1px solid #e5e7eb', borderRadius: 12, padding: 8 }}>
      <div style={{ fontWeight: 700, color: '#0a2463', marginBottom: 4, textAlign: 'center' }}>{name}</div>
      {loading ? (
        <div style={{ textAlign: 'center', color: '#666' }}>Загрузка...</div>
      ) : data.length > 0 ? (
        <TrendChart compact height={120} yMax={10} yStep={2} label={name} points={data.map((p: any) => ({ date: p.date, hpi: Number(p.score) }))} />
      ) : (
        <div style={{ textAlign: 'center', color: '#777', padding: '20px 0' }}>Нет данных</div>
      )}
    </div>
  );
};

export default function DashboardPage() {
  const navigate = useNavigate();
  const { isBasicSurveyComplete } = useSurvey();
  
  // Дополнительная проверка завершения базовой диагностики
  if (!isBasicSurveyComplete) {
    return <Navigate to="/account/diagnostics" replace state={{ message: 'Для доступа к дашборду необходимо завершить базовую диагностику.' }} />;
  }

  const [showSurveyNotification, setShowSurveyNotification] = useState(false);

  useEffect(() => {
    // Показываем уведомление только если опрос не пройден
    // !isBasicSurveyComplete -> true, если опрос НЕ пройден
    if (!isBasicSurveyComplete) {
      setShowSurveyNotification(true);
    }
  }, [isBasicSurveyComplete]);
  
  const location = useLocation();
  const { selectedDate, setSelectedDate } = useSurvey();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dashboard, setDashboard] = useState<any>(null);
  const [radarResp, setRadarResp] = useState<any>(null);
  const [trendResp, setTrendResp] = useState<any>(null);
  const [recsLoading, setRecsLoading] = useState<boolean>(false);
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [recsCollapsed, setRecsCollapsed] = useState<boolean>(true);
  const [sphereDynamicsCollapsed, setSphereDynamicsCollapsed] = useState<boolean>(true);

  // Use the date from context as the main source of truth.
  // The URL parameter is used to initialize the state on first load.
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const dateFromUrl = params.get('date');
    if (dateFromUrl) {
      const correctedDate = parseYmd(dateFromUrl);

      if (correctedDate && !isNaN(correctedDate.getTime())) {
        const contextDateStr = selectedDate ? `${selectedDate.getFullYear()}-${String(selectedDate.getMonth() + 1).padStart(2, '0')}-${String(selectedDate.getDate()).padStart(2, '0')}` : undefined;
        if (dateFromUrl !== contextDateStr) {
          setSelectedDate(correctedDate);
        }
      }
    }
  }, [location.search, selectedDate, setSelectedDate]);

  const dateStr = useMemo(() => {
    const d = selectedDate || new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  }, [selectedDate]);

  const monthStr = useMemo(() => {
    const params = new URLSearchParams(location.search);
    return params.get('month');
  }, [location.search]);

  const displayDate = useMemo(() => {
    const d = dateStr ? new Date(dateStr) : new Date();
    if (Number.isNaN(d.getTime())) return '';
    return d.toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric' });
  }, [dateStr]);
  
  const selectedDateObj = useMemo(() => (dateStr ? new Date(dateStr) : new Date()), [dateStr]);

  useEffect(() => {
      setLoading(true);
      setError(null);
      
    setRecsLoading(true);
    console.log('🔄 Загружаем дашборд для даты:', dateStr);
    
    Promise.all([
      apiClient.getDashboard(dateStr),
      apiClient.getRadar(dateStr),
      apiClient.getTrend(monthStr || undefined, dateStr),
      apiClient.getRecommendations(dateStr),
    ])
      .then(([d, r, t, recsResp]) => {
        console.log('✅ API ответы получены:');
        console.log('Dashboard:', d);
        console.log('Radar:', r);
        console.log('Trend:', t);
        console.log('Recommendations:', recsResp);
        
        setDashboard(d);
        setRadarResp(r);
        setTrendResp(t);
        
        // Исправляем обработку рекомендаций - API возвращает { recommendations: [...] }
        let recommendations: any[] = [];
        if (recsResp) {
          if (Array.isArray(recsResp)) {
            recommendations = recsResp;
          } else if (Array.isArray(recsResp.recommendations)) {
            recommendations = recsResp.recommendations;
          } else if (Array.isArray(recsResp.items)) {
            recommendations = recsResp.items;
          } else if (Array.isArray(recsResp.data)) {
            recommendations = recsResp.data;
          }
        }
        
        console.log('🔍 Обработанные рекомендации:', recommendations);
        
        setRecs(recommendations as Recommendation[]);
      })
      .catch((e) => {
        console.error('❌ Ошибка загрузки дашборда:', e);
        setError((e as any)?.message || 'Не удалось загрузить дашборд');
      })
      .finally(() => { 
      setLoading(false);
        setRecsLoading(false); 
        console.log('🏁 Загрузка завершена');
      });
  }, [dateStr]);

  // Авто-фолбэк: если данных на выбранную дату нет, открыть последнюю дату с активностью в месяце
  useEffect(() => {
    if (loading) return;
    const noData = !dashboard || (dashboard && (dashboard.hpi == null || Number(dashboard.hpi) === 0));
    if (!noData) return;

    const d = selectedDate || new Date();
    const from = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2,'0')}-01`;
    const to = new Date(d.getFullYear(), d.getMonth() + 1, 0);
    const toStr = `${to.getFullYear()}-${String(to.getMonth() + 1).padStart(2,'0')}-${String(to.getDate()).padStart(2,'0')}`;

    (async () => {
      try {
        const statuses = await apiClient.getCalendarStatus(from, toStr);
        const activeDates = (statuses || [])
          .filter((s: any) => {
            const basicDone = s?.basic?.status === 'complete' || (!!s?.basic?.total && s.basic.answered > 0);
            const proDone = s?.pro?.status === 'complete' || (!!s?.pro?.total && s.pro.answered > 0);
            return basicDone || proDone;
          })
          .map((s: any) => s.date)
          .sort();
        if (activeDates.length === 0) return;
        const target = activeDates
          .filter((ds: string) => ds <= dateStr)
          .pop() || activeDates[activeDates.length - 1];
        if (target && target !== dateStr) {
          console.log('↪️ Авто-переход на дату с данными:', target);
          const nd = new Date(target);
          setSelectedDate(nd);
          const params = new URLSearchParams(location.search);
          params.set('date', target);
          navigate(`${location.pathname}?${params.toString()}`, { replace: true });
        }
      } catch (e) {
        console.warn('Не удалось выполнить фолбэк по календарю:', e);
      }
    })();
  }, [loading, dashboard, dateStr, selectedDate, navigate, location.pathname, location.search, setSelectedDate]);

  const hpiValue: number | null = useMemo(() => {
    if (!dashboard) return null;
    return Number(dashboard.hpi ?? dashboard.value ?? 0);
  }, [dashboard]);

  const trendPoints: any[] = useMemo(() => {
    if (!trendResp) return [];
    if (Array.isArray(trendResp)) return trendResp;
    if (Array.isArray(trendResp.points)) return trendResp.points;
    if (Array.isArray(trendResp.data)) return trendResp.data;
    if (Array.isArray(trendResp.trend)) return trendResp.trend;
    if (dashboard && Array.isArray(dashboard.trend)) return dashboard.trend;
    return [];
  }, [trendResp, dashboard]);

  const radarItems: { name: string; value: number }[] = useMemo(() => {
    if (!radarResp) return [];
    
    const out: { name: string; value: number }[] = [];
    const obj = (radarResp.radar ?? radarResp);
    if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
      SPHERE_ORDERED.forEach((s, idx) => {
        const k = String(idx + 1);
        if (obj[k] != null || obj[idx + 1] != null) out.push({ name: s.name, value: Number(obj[k] ?? obj[idx + 1]) });
      });
      if (out.length) return out;
      Object.entries(obj).forEach(([k, v]) => out.push({ name: k, value: Number(v) }));
      return out;
    }
    const arr = Array.isArray(radarResp.items) ? radarResp.items : Array.isArray(radarResp.data) ? radarResp.data : Array.isArray(radarResp) ? radarResp : [];
    if (arr.length > 0) {
      return arr.map((r: any, i: number) => ({ name: r.name ?? r.label ?? `Сфера ${i + 1}`, value: Number(r.value ?? r.score ?? 0) }));
    }
    return [];
  }, [radarResp]);

  const prevHpi: number | null = useMemo(() => {
    try {
      if (!trendPoints || trendPoints.length === 0) return null;
      const points = trendPoints
        .map((p: any) => ({
          date: new Date(p.date || p.dt || p[0]),
          hpi: Number(p.hpi ?? p.value ?? p[1] ?? 0),
        }))
        .filter(pt => !Number.isNaN(pt.date.getTime()))
        .sort((a, b) => a.date.getTime() - b.date.getTime());
      let prev: number | null = null;
      for (let i = points.length - 1; i >= 0; i -= 1) {
        const pt = points[i];
        if (dateStr && pt.date.getTime() === selectedDateObj.getTime()) {
          if (i - 1 >= 0) prev = points[i - 1].hpi;
          break;
        }
        if (pt.date < selectedDateObj) { prev = pt.hpi; break; }
      }
      return prev;
    } catch { return null; }
  }, [trendPoints, selectedDateObj, dateStr]);

  const deltaPercent: number | null = useMemo(() => {
    if (hpiValue == null || prevHpi == null || prevHpi === 0) return null;
    return ((hpiValue - prevHpi) / prevHpi) * 100;
  }, [hpiValue, prevHpi]);

  // Вспомогательная функция: человекочитаемое имя сферы из объекта рекомендации
  const getSphereName = useCallback((r: any): string => {
    const raw = r?.sphere ?? r?.sphere_id ?? r?.sphereId ?? r?.data?.sphere;
    if (raw == null) return '';
    const num = Number(raw);
    if (Number.isFinite(num) && num >= 1 && num <= SPHERE_ORDERED.length) return SPHERE_ORDERED[num - 1].name;
    if (typeof raw === 'string') {
      const byId = SPHERE_ORDERED.find(s => s.id === raw || s.name === raw);
      return byId?.name || raw;
    }
    return '';
  }, []);

  // Вспомогательная функция: эмодзи сферы из объекта рекомендации
  const getSphereEmoji = useCallback((r: any): string => {
    const raw = r?.sphere ?? r?.sphere_id ?? r?.sphereId ?? r?.data?.sphere;
    if (raw == null) return '💡';
    const num = Number(raw);
    if (Number.isFinite(num) && num >= 1 && num <= SPHERE_ORDERED.length) return SPHERE_ORDERED[num - 1].emoji;
    if (typeof raw === 'string') {
      const byId = SPHERE_ORDERED.find(s => s.id === raw || s.name === raw);
      return byId?.emoji || '💡';
    }
    return '💡';
  }, []);

  // Убираем повторы: оставляем по одной базовой рекомендации на сферу
  const uniqueRecsBySphere = useMemo(() => {
    const seen = new Set<string>();
    const out: any[] = [];
    (recs || []).forEach((r: any) => {
      const key = String(r?.sphere ?? r?.sphere_id ?? r?.sphereId ?? '');
      if (key && !seen.has(key)) {
        seen.add(key);
        out.push(r);
      }
    });
    
    // Если нет рекомендаций от API, создаем базовые
    if (out.length === 0) {
      return SPHERE_ORDERED.map((s, idx) => ({
        sphere: String(idx + 1),
        title: `Развивайте сферу: ${s.name}`,
        text: '1 конкретный шаг на 15–20 минут сегодня.',
        description: '1 конкретный шаг на 15–20 минут сегодня.'
      }));
    }
    
    return out;
  }, [recs]);

  if (loading) return <div>Загрузка дашборда...</div>;
  if (error) return <div className={styles.error}>{error}</div>;

  return (
    <div className={styles.dashboardContainer}>
      <ProBasicHeader variant="dashboards" dateText={displayDate} />

      <div className={styles.hpiCard}>
        <h2>Итоговый HPI</h2>
        {hpiValue != null ? (
          <div className={styles.hpiDisplay}>
            <div className={styles.hpiValue}>{hpiValue.toFixed(1)}</div>
            {deltaPercent != null && Number.isFinite(deltaPercent) ? (
              <div className={`${styles.hpiChange} ${deltaPercent >= 0 ? styles.positive : styles.negative}`}>
                {deltaPercent >= 0 ? '▲' : '▼'} {Math.abs(deltaPercent).toFixed(1)}%
              </div>
            ) : null}
              </div>
        ) : (
          <div style={{ textAlign: 'center', color: '#777', padding: '20px 0' }}>Нет данных</div>
          )}
        </div>

      <section className={styles.chartCard}>
        <h2 className={styles.cardTitle}>Динамика</h2>
        <div>
          {trendPoints.length > 0 ? (
            <TrendChart points={trendPoints.map((p: any) => ({ date: p.date || p.dt || p[0], hpi: Number(p.hpi ?? p.value ?? p[1] ?? 0) }))} />
          ) : (
            <div style={{ textAlign: 'center', color: '#777', padding: '20px 0' }}>Нет данных</div>
          )}
        </div>
      </section>

      <section className={styles.chartCard}>
        <h2 className={styles.cardTitle}>Баланс по сферам</h2>
        <div>
          {radarItems.length > 0 ? (
            <RadarChart data={radarItems} />
          ) : (
            <div style={{ textAlign: 'center', color: '#777', padding: '20px 0' }}>Нет данных</div>
          )}
        </div>
      </section>

      {/* Compact per-sphere trends grid under HPI trend */}
      <section className={styles.chartCard}>
        <h2 className={`${styles.cardTitle} ${styles.toggleTitle}`} onClick={() => setSphereDynamicsCollapsed((v: boolean) => !v)}>
          <span className={`${styles.chevron} ${!sphereDynamicsCollapsed ? styles.open : ''}`}></span>
          Динамика по сферам
        </h2>
        {!sphereDynamicsCollapsed && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12, marginTop: '1rem' }}>
            {SPHERE_ORDERED.map((s, idx) => {
              const id = String(idx + 1);
              const params = monthStr ? { month: monthStr } : (dateStr ? { date: dateStr } : {});
              const radarValue = radarItems.find(item => item.name === s.name)?.value;
              return (
                <SphereTrendMini key={id} id={id} name={s.name} params={params} radarValue={radarValue} />
              );
            })}
          </div>
        )}
      </section>

      <section className={styles.chartCard}>
        <h2 className={`${styles.cardTitle} ${styles.toggleTitle}`} onClick={() => setRecsCollapsed((v: boolean) => !v)}>
          <span className={`${styles.chevron} ${!recsCollapsed ? styles.open : ''}`}></span>
          Базовые рекомендации
        </h2>
        {!recsCollapsed && (recsLoading ? (
          <div className={styles.recsGrid}>
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className={styles.recCard} style={{ opacity: 0.6 }}>
                <div style={{ height: 16, width: '60%', background: 'var(--background-color)', borderRadius: 6 }} />
                <div style={{ height: 12, width: '90%', background: 'var(--background-color)', borderRadius: 6, marginTop: 8 }} />
                <div style={{ height: 12, width: '70%', background: 'var(--background-color)', borderRadius: 6, marginTop: 6 }} />
                    </div>
                  ))}
          </div>
        ) : (uniqueRecsBySphere && uniqueRecsBySphere.length > 0) ? (
          <div className={styles.recsGrid}>
            {uniqueRecsBySphere.map((r: any, idx: number) => (
              <div key={idx} className={styles.recCard}>
                <div className={styles.recHeader}>
                  <div className={styles.recIcon}>{getSphereEmoji(r)}</div>
                  <div className={styles.recTitle}>{r.title ?? r.name ?? r?.data?.title ?? r?.data?.data?.title ?? 'Рекомендация'}</div>
                </div>
                <div className={styles.recText}>{r.text ?? r.description ?? r.suggestion ?? r?.data?.description ?? r?.data?.data?.description ?? ''}</div>
            </div>
            ))}
        </div>
        ) : (
          <div style={{ textAlign: 'center', color: '#777', padding: '20px 0' }}>Нет данных</div>
        ))}
      </section>
    </div>
  );
} 