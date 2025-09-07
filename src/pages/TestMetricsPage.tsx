import React, { useState } from 'react';
import ProMetricsForm from '../components/ProMetricsForm';
import { testMetricsData } from '../data/testMetricsData';
import styles from './ProSurveyPage.module.css';

export default function TestMetricsPage() {
  const [answers, setAnswers] = useState<Record<string, any>>({});
  
  const handleAnswerChange = (metricName: string, field: string, value: string | number) => {
    console.log('Metric change:', metricName, field, value);
    
    // Создаем ключ для метрики
    const metricsKey = 'metrics-love';
    
    // Получаем текущий ответ или создаем новый
    const currentAnswer = answers[metricsKey] || {};
    
    // Парсим существующие данные или создаем новые
    let metricsData = {};
    try {
      if (currentAnswer.text) {
        metricsData = JSON.parse(currentAnswer.text);
      }
    } catch {}
    
    // Обновляем конкретное поле
    metricsData[field] = value;
    
    // Создаем новый ответ
    const newAnswer = {
      ...currentAnswer,
      text: JSON.stringify(metricsData)
    };
    
    // Обновляем состояние
    setAnswers(prev => ({
      ...prev,
      [metricsKey]: newAnswer
    }));
  };

  const sphereInfo = {
    id: 'love',
    name: 'Отношения с любимыми',
    emoji: '💖'
  };

  return (
    <div className={styles.container}>
      <h1>Тест формы метрик</h1>
      <ProMetricsForm
        sphere={sphereInfo}
        metrics={testMetricsData.love.metrics}
        answers={answers}
        onAnswerChange={handleAnswerChange}
      />
      
      <div style={{ marginTop: '20px', padding: '20px', backgroundColor: '#f5f5f5' }}>
        <h3>Текущие ответы:</h3>
        <pre>{JSON.stringify(answers, null, 2)}</pre>
      </div>
    </div>
  );
} 