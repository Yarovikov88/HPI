import React, { useEffect, useState } from 'react';
// import { apiClient } from '../services/api';
import styles from './HistoryPage.module.css';
import { Link } from 'react-router-dom';


const HistoryPage: React.FC = () => {
    const [loading, setLoading] = useState(false); // Убрали загрузку
    const [error, setError] = useState<string | null>(null);

    // Вся логика загрузки отключена
    useEffect(() => {
      console.warn('History page data fetching is disabled.');
    }, []);

    if (loading) {
      return <div>Загрузка истории...</div>;
    }
  
    if (error) {
      return <div>{error}</div>;
    }

    return (
        <div className={styles.container}>
            <h1 className={styles.title}>История ответов</h1>
            <p>Раздел временно недоступен.</p>
        </div>
    );
};

export default HistoryPage; 