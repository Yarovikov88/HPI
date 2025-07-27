import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
// import { apiClient } from '../services/api';
import styles from './DashboardPage.module.css';

export default function DashboardPage() {
  const location = useLocation();
  const [loading, setLoading] = useState(true);
  // const [data, setData] = useState<any>(null);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const dateStr = params.get("date") || undefined;
    setLoading(true);
    console.warn('Data fetching is disabled in DashboardPage.');
    // apiClient.getDashboardData(dateStr)
    //     .then(response => {
    //         setData(response);
    //     })
    //     .finally(() => {
    //         setLoading(false);
    //     });
    setLoading(false);
  }, [location.search]);

  if (loading) {
    return <div>Загрузка дашборда...</div>;
  }

  // if (error) {
  //   return <div>{error}</div>;
  // }
  
  // Здесь будет логика отображения данных basicData и proData
  // Пока просто выведем то, что получили

  return (
    <div className={styles.dashboardContainer}>
      <h1 className={styles.title}>Дашборд</h1>

      {/* {basicData && (
        <section className={styles.card}>
          <h2 className={styles.cardTitle}>Базовый дашборд</h2>
          <div className={styles.metric}>
            <strong>Индекс HPI:</strong> {basicData.hpi.toFixed(1)}
          </div>
          {basicData.hpi_change !== null && (
            <div className={styles.metric}>
              <strong>Изменение HPI:</strong> {basicData.hpi_change > 0 ? `+${basicData.hpi_change.toFixed(1)}` : basicData.hpi_change.toFixed(1)}
            </div>
          )}
          {basicData.trend && basicData.trend.length > 0 && (
            <div>
              <h3 className={styles.trendTitle}>Тренд HPI:</h3>
              <ul className={styles.trendList}>
                {basicData.trend.map((item, index) => (
                  <li key={index}>
                    {new Date(item.date).toLocaleDateString()}: <strong>{item.hpi.toFixed(1)}</strong>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )} */}

      {/* {proData && (
        <section className={styles.card}>
          <h2 className={styles.cardTitle}>Pro дашборд</h2>
          {/* Сюда можно будет добавить красивое отображение Pro данных */}
          {/* <p>Данные Pro-дашборда успешно загружены.</p>
        </section>
      )} */}

      {/* {!basicData && !proData && !error && (
         <p>Нет данных для отображения.</p>
      )} */}
    </div>
  );
} 