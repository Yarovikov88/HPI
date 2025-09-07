import React, { useState, useEffect } from 'react';
import { useLocation, Navigate } from 'react-router-dom';
import { useSurvey } from '../hooks/useSurvey';
import { apiClient } from '../services/api';
import type { ProAnswer } from '../contexts/types';
import { SPHERE_ORDERED } from '../data/spheres';
import { proSections } from '../data/proSections';
import { ProBasicHeader } from '../components/ProBasicHeader';
import styles from './ProDashboardPage.module.css';

// Используем правильные категории из proSections
const PRO_CATEGORIES: { key: string; title: string; icon: string }[] = [
  { key: 'problems', title: 'Проблемы', icon: '🔍' },
  { key: 'goals', title: 'Цели', icon: '🎯' },
  { key: 'blockers', title: 'Блокеры', icon: '🚫' },
  { key: 'metrics', title: 'Метрики', icon: '📊' },
  { key: 'achievements', title: 'Достижения', icon: '🏆' },
];

export default function ProDashboardPage() {
  const location = useLocation();
  const { selectedDate, isProSurveyComplete } = useSurvey();
  
  if (!isProSurveyComplete) {
    return <Navigate to="/account/diagnostics" replace state={{ message: 'Для доступа к PRO дашборду необходимо завершить PRO диагностику.' }} />;
  }

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [proByCategory, setProByCategory] = useState<Record<string, ProAnswer[]>>({});
  const [completionStatus, setCompletionStatus] = useState<any>(null);
  
  // HPI данные
  const [hpiValue, setHpiValue] = useState<number | null>(null);
  const [hpiChange, setHpiChange] = useState<number | null>(null);
  
  // Отдельное состояние для категорий PRO
  const [categoriesCollapsed, setCategoriesCollapsed] = useState<Record<string, boolean>>(() => {
    const init: Record<string, boolean> = {};
    PRO_CATEGORIES.forEach(c => { 
      init[c.key] = true; // true = свернуто, false = развернуто
    });
    return init;
  });
  
  // Отдельное состояние для AI рекомендаций
  const [aiRecsCollapsed, setAiRecsCollapsed] = useState<boolean>(true);
  const [aiRecsBySphere, setAiRecsBySphere] = useState<Record<string, { title?: string; name?: string; text?: string; description?: string; suggestion?: string }[]>>({});
  const [aiLoading, setAiLoading] = useState<boolean>(false);
  const [generatingAi, setGeneratingAi] = useState<boolean>(false);

  const params = new URLSearchParams(location.search);
  const getLocalYMD = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  
  const dateStr = selectedDate ? getLocalYMD(selectedDate) : (params.get('date') || getLocalYMD(new Date()));
  const displayDate = new Date(dateStr).toLocaleDateString('ru-RU');

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      setError(null);
      try {
        // Загружаем статус завершенности
        const status = await apiClient.getProCompletionStatus(dateStr);
        setCompletionStatus(status);
        
        // Загружаем HPI данные
        const dashboard = await apiClient.getDashboard(dateStr);
        if (dashboard) {
          setHpiValue(Number(dashboard.hpi ?? dashboard.value ?? 0));
          
          // Загружаем тренд для расчета изменения
          const trend = await apiClient.getTrend(dateStr);
          if (trend && Array.isArray(trend)) {
            const points = trend
              .map((p: any) => ({
                date: new Date(p.date || p.dt || p[0]),
                hpi: Number(p.hpi ?? p.value ?? p[1] ?? 0),
              }))
              .filter(pt => !Number.isNaN(pt.date.getTime()))
              .sort((a, b) => a.date.getTime() - b.date.getTime());
            
            const currentDate = new Date(dateStr);
            let prevHpi: number | null = null;
            for (let i = points.length - 1; i >= 0; i -= 1) {
              const pt = points[i];
              if (pt.date < currentDate) { 
                prevHpi = pt.hpi; 
                break; 
              }
            }
            
            if (prevHpi && prevHpi !== 0) {
              const change = ((Number(dashboard.hpi ?? dashboard.value ?? 0) - prevHpi) / prevHpi) * 100;
              setHpiChange(change);
            }
          }
        }
        
        const allData: Record<string, ProAnswer[]> = {};
        
        // Загружаем данные для каждой категории за конкретную дату
        for (const category of PRO_CATEGORIES) {
          try {
            const data = await apiClient.getProAnswers(category.key, dateStr);
            allData[category.key] = data || [];
          } catch (err) {
            allData[category.key] = [];
          }
        }
        
        setProByCategory(allData);
      } catch (err) {
        setError('Ошибка загрузки данных');
      } finally {
        setLoading(false);
      }
    };

    fetchAll();
  }, [dateStr]);

  useEffect(() => {
    // Загружаем AI-рекомендации с автоматической генерацией
    const loadAi = async () => {
      setAiLoading(true);
      try {
        // Сначала пробуем загрузить существующие рекомендации
        const data: any = await apiClient.getRecommendations(dateStr);
        
        const arr: any[] = Array.isArray(data) ? data : (Array.isArray(data?.items) ? data.items : []);
        
        // Если рекомендаций нет, автоматически генерируем их
        if (arr.length === 0) {
          setGeneratingAi(true);
          try {
            const generatedData = await apiClient.generateAiRecommendations(dateStr);
            if (generatedData && generatedData.ai_recommendations) {
              // Используем сгенерированные рекомендации
              const generatedArr = generatedData.ai_recommendations;
              const grouped = groupRecommendationsBySphere(generatedArr);
              setAiRecsBySphere(grouped);
              return;
            }
          } catch (genError) {
            // Ошибка генерации
          } finally {
            setGeneratingAi(false);
          }
        }
        
        // Группируем существующие рекомендации
        const grouped = groupRecommendationsBySphere(arr);
        setAiRecsBySphere(grouped);
      } catch (error) {
        setAiRecsBySphere({});
      } finally {
        setAiLoading(false);
      }
    };
    loadAi();
  }, [dateStr]);

  // Функция для группировки рекомендаций по сферам
  const groupRecommendationsBySphere = (arr: any[]): Record<string, any[]> => {
    const grouped: Record<string, any[]> = {};
    arr.forEach((raw: any) => {
      const sphereRaw = raw?.sphere ?? raw?.sphere_name ?? raw?.sphereId ?? raw?.sphere_id;
      let sphereLabel: string = 'Общее';
      if (sphereRaw != null) {
        const num = Number(sphereRaw);
        if (Number.isFinite(num) && num >= 1 && num <= SPHERE_ORDERED.length) {
          sphereLabel = SPHERE_ORDERED[num - 1].name;
        } else if (typeof sphereRaw === 'string') {
          sphereLabel = sphereRaw;
        }
      }
      const title = (raw?.title ?? raw?.name ?? raw?.data?.title ?? raw?.data?.data?.title ?? 'Рекомендация');
      const text = (raw?.text ?? raw?.description ?? raw?.suggestion ?? raw?.data?.description ?? raw?.data?.data?.description ?? '');
      const steps = Array.isArray(raw?.data?.action_steps) ? raw.data.action_steps : (Array.isArray(raw?.action_steps) ? raw.action_steps : []);
      const metrics = (raw?.data?.metrics ?? raw?.metrics ?? null);
      const priority = (raw?.priority ?? raw?.data?.priority ?? null);
      const rtype = (raw?.type ?? raw?.data?.type ?? null);
      const item = { title, text, steps, metrics, priority, type: rtype };
      if (!grouped[sphereLabel]) grouped[sphereLabel] = [];
      grouped[sphereLabel].push(item);
    });
    return grouped;
  };

  const sphereNameByAnswer = (ans: ProAnswer): string => {
    const sphereNum = Number(ans.sphere);
    return (sphereNum >= 1 && sphereNum <= SPHERE_ORDERED.length) ? SPHERE_ORDERED[sphereNum - 1].name : `Сфера ${sphereNum}`;
  };

  const handleGenerateAiRecommendations = async () => {
    setGeneratingAi(true);
    try {
      // Генерируем AI рекомендации
      const generatedData = await apiClient.generateAiRecommendations(dateStr);
      if (generatedData && generatedData.ai_recommendations) {
        // Группируем и обновляем состояние
        const grouped = groupRecommendationsBySphere(generatedData.ai_recommendations);
        setAiRecsBySphere(grouped);
      }
    } catch (error) {
      console.error('Error generating AI recommendations:', error);
      alert('Ошибка генерации AI рекомендаций. Попробуйте позже.');
    } finally {
      setGeneratingAi(false);
    }
  };

  // Функция для проверки, есть ли данные в категории
  const hasCategoryData = (categoryKey: string): boolean => {
    if (!completionStatus || !completionStatus.spheres) return false;
    
    // Проверяем, есть ли хотя бы одна сфера с данными для этой категории
    return Object.values(completionStatus.spheres).some((sphere: any) => 
      sphere.categories && sphere.categories[categoryKey] && sphere.categories[categoryKey].has_answer
    );
  };

  // Функция для правильного отображения текста ответа
  const getDisplayText = (item: any): string => {
    if (!item.text) return '';
    
    // Если это JSON-строка, пытаемся парсить
    if (typeof item.text === 'string' && item.text.startsWith('{')) {
      try {
        const parsed = JSON.parse(item.text);
        // Если это метрики, извлекаем what_measure
        if (parsed.what_measure) {
          return parsed.what_measure;
        }
        // Если есть другие поля, объединяем их
        const textParts = [];
        if (parsed.what_measure) textParts.push(parsed.what_measure);
        if (parsed.target_value !== undefined) textParts.push(`Цель: ${parsed.target_value}`);
        if (parsed.unit) textParts.push(`Единица: ${parsed.unit}`);
        return textParts.join(' | ');
      } catch (e) {
        // Если не JSON, возвращаем как есть
        return item.text;
      }
    }
    
    return item.text;
  };

  const handleCategoryToggle = (categoryKey: string) => {
    console.log('🔍 Toggling category:', categoryKey);
    console.log('🔍 Current categories collapsed state:', categoriesCollapsed);
    setCategoriesCollapsed((prev: Record<string, boolean>) => {
      const newState = { ...prev, [categoryKey]: !prev[categoryKey] };
      console.log('🔍 New categories collapsed state:', newState);
      return newState;
    });
  };

  const handleAiRecsToggle = () => {
    console.log('🔍 Toggling AI recs, current state:', aiRecsCollapsed);
    setAiRecsCollapsed((prev: boolean) => !prev);
  };

  if (loading) {
    return <div className={styles.loading}>Загрузка...</div>;
  }

  if (error) {
    return <div className={styles.error}>Ошибка: {error}</div>;
  }

  return (
    <div className={styles.dashboardContainer}>
      <ProBasicHeader variant="dashboards" dateText={displayDate} />

      {/* Фиксированный HPI блок по центру - ВСЕГДА ВИДИМЫЙ */}
      <div className={styles.fixedHpiContainer}>
        <div className={styles.hpiCard}>
          <h2>Итоговый HPI</h2>
          {hpiValue != null ? (
            <div className={styles.hpiDisplay}>
              <div className={styles.hpiValue}>{hpiValue.toFixed(1)}</div>
              {hpiChange != null && Number.isFinite(hpiChange) ? (
                <div className={`${styles.hpiChange} ${hpiChange >= 0 ? styles.positive : styles.negative}`}>
                  {hpiChange >= 0 ? '▲' : '▼'} {Math.abs(hpiChange).toFixed(1)}%
                </div>
              ) : null}
            </div>
          ) : (
            <div className={styles.hpiDisplay}>
              <div className={styles.hpiValue}>0.0</div>
              <div className={styles.hpiChange}>Нет данных</div>
            </div>
          )}
        </div>
      </div>

      <section className={styles.chartCard}>
        <h2 className={styles.cardTitle}>Категории PRO</h2>
        <div className={styles.categoriesGrid}>
          {PRO_CATEGORIES.map((category) => {
            const items = proByCategory[category.key] || [];
            const hasData = hasCategoryData(category.key);
            const isCollapsed = categoriesCollapsed[category.key];
            
            return (
              <div key={`category-${category.key}`} className={styles.categoryCard}>
                <div 
                  className={styles.categoryHeader}
                  onClick={() => handleCategoryToggle(category.key)}
                >
                  <div className={styles.categoryIcon}>{category.icon}</div>
                  <div className={styles.categoryInfo}>
                    <div className={styles.categoryTitle}>{category.title}</div>
                    <div className={styles.categoryCount}>
                      {hasData ? '✓' : '○'} {items.length} элементов
                    </div>
                  </div>
                  <span className={`${styles.chevron} ${!isCollapsed ? styles.open : ''}`}></span>
                </div>
                
                {!isCollapsed && (
                  <div className={styles.itemsList}>
                    {items.length > 0 ? (
                      items.map((item: ProAnswer, index: number) => (
                        <div key={`${category.key}-${index}`} className={styles.itemCard}>
                          <div className={styles.itemHeader}>
                            <span className={styles.sphereName}>{sphereNameByAnswer(item)}</span>
                            <span className={styles.itemDate}>
                              {new Date(item.date).toLocaleDateString('ru-RU')}
                            </span>
                          </div>
                          <div className={styles.itemText}>{getDisplayText(item)}</div>
                        </div>
                      ))
                    ) : (
                      <div className={styles.emptyState}>Нет данных</div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      <section className={styles.chartCard}>
        <h2 className={`${styles.cardTitle} ${styles.toggleTitle}`} onClick={handleAiRecsToggle}>
          <span className={`${styles.chevron} ${!aiRecsCollapsed ? styles.open : ''}`}></span>
          AI рекомендации
        </h2>
        {!aiRecsCollapsed && (
          <div className={styles.recsGrid}>
            {aiLoading || generatingAi ? (
              <div className={styles.loadingState}>
                {generatingAi ? 'Генерируем AI рекомендации...' : 'Загрузка AI рекомендаций...'}
              </div>
            ) : Object.keys(aiRecsBySphere).length > 0 ? (
              Object.values(aiRecsBySphere).flat().map((r: any, j: number) => (
                <div key={j} className={styles.recCard}>
                  <div className={styles.recHeader}>
                    <div className={styles.recIcon}>🤖</div>
                    <div className={styles.recTitle}>{r.title || 'AI Рекомендация'}</div>
                  </div>
                  <div className={styles.recText}>{r.text || r.description || 'Описание рекомендации'}</div>
                </div>
              ))
            ) : (
              <div className={styles.emptyState}>
                <p>Пока нет AI рекомендаций</p>
                <button 
                  className={styles.generateButton}
                  onClick={handleGenerateAiRecommendations}
                  disabled={generatingAi}
                >
                  {generatingAi ? 'Генерируем...' : 'Сгенерировать AI рекомендации'}
                </button>
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
} 