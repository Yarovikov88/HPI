import React, { useState, useEffect } from 'react';
// import { apiClient, type ProDashboardData } from '../services/api';
import { useLocation } from 'react-router-dom';
import styles from './ProDashboardPage.module.css';

export default function ProDashboardPage() {
    const location = useLocation();
    // const [data, setData] = useState<ProDashboardData | null>(null);
    const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
        const params = new URLSearchParams(location.search);
        const dateStr = params.get("date") || undefined;
        setLoading(true);
        console.warn('Data fetching is disabled in ProDashboardPage.');
        // apiClient.getProDashboardData(dateStr)
        //     .then(response => {
        //         setData(response);
        //         setLoading(false);
        //     })
        //     .catch(error => {
        //         console.error("Failed to fetch pro dashboard data:", error);
        //         setLoading(false);
        //     });
        setLoading(false); // Убираем загрузку
    }, [location.search]);

  if (loading) {
        return <div>Загрузка Pro-дашборда...</div>;
  }

  if (error) {
        return <div>{error}</div>;
  }
  
    // if (!data) {
    //     return <div>Нет данных для отображения за выбранную дату.</div>;
    // }

    return (
        <div className={styles.container}>
            <h2>Pro-дашборд</h2>
            {/* <div className={styles.radarChart}>
                <h3>Радар компетенций</h3>
                <p>Здесь будет график-радар.</p>
            </div>
            <div className={styles.trendChart}>
                <h3>Динамика</h3>
                <p>Здесь будет график динамики.</p>
            </div> */}
        </div>
    );
} 