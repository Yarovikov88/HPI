import React, { useState } from 'react';
import styles from './DataSeeder.module.css';
// import { useSurvey } from '../hooks/useSurvey';
// import { apiClient } from '../services/api'; // Импортируем наш клиент

// Список доступных сценариев. 
// Ключ - то, что пойдет на бэкенд, значение - то, что увидит пользователь.
const SCENARIOS = {
  'burnout': 'Сценарий: Проф. выгорание',
  'growth': 'Сценарий: Личностный рост',
  // TODO: Добавить сюда больше сценариев, когда они появятся на бэкенде
};

const DataSeeder: React.FC = () => {
  // const { setAnswersFromApi, setProAnswersFromApi, refetchAllData } = useSurvey(); // Получаем новые функции
  const [selectedScenario, setSelectedScenario] = useState(Object.keys(SCENARIOS)[0]);
  const [isLoading, setIsLoading] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const userId = 1; // Захардкодим ID тестового пользователя

  const handleSeed = async () => {
    setIsLoading(true);
    setFeedbackMessage('');

    try {
      // Сначала убедимся, что все вопросы загружены
      // await refetchAllData();

      // Используем apiClient вместо fetch
      console.warn('Data seeding is temporarily disabled.');
      // const result = await apiClient.seedScenario(userId, selectedScenario);
      
      // console.log("Полученные данные:", result);
      
      // Прямое обновление состояния из полученных данных
      // if (result && result.answers && result.pro_answers) {
      //   setAnswersFromApi(result.answers || []);
      //   setProAnswersFromApi(result.pro_answers || []);
      //   setFeedbackMessage('Данные успешно сгенерированы!');
        
        // УБИРАЕМ ПЕРЕНАПРАВЛЕНИЕ
        // setTimeout(() => {
        //   navigate('/dashboard');
        // }, 1500);

      // } else {
        // setFeedbackMessage('Сценарий выполнен, но в ответе нет необходимых данных.');
        // console.error("Неожиданный формат ответа от сервера:", result);
      // }

    } catch (error: any) {
      // Улучшенная обработка ошибок для Axios
      if (error.response) {
        console.error("Server error response:", error.response.data);
        const detail = error.response.data?.detail || 'Произошла ошибка на сервере';
        setFeedbackMessage(`Ошибка: ${detail}`);
      } else {
        console.error("Network or other error:", error.message);
        setFeedbackMessage(`Ошибка сети: ${error.message}`);
      }
    } finally {
      // Сбрасываем isLoading через некоторое время, чтобы пользователь успел прочитать сообщение
      setTimeout(() => setIsLoading(false), 1500);
    }
  };

  return (
    <div className={styles.container}>
      <select 
        value={selectedScenario}
        onChange={(e) => setSelectedScenario(e.target.value)}
        disabled={isLoading}
        className={styles.select}
      >
        {Object.entries(SCENARIOS).map(([key, value]) => (
          <option key={key} value={key}>{value}</option>
        ))}
      </select>
      <button 
        onClick={handleSeed} 
        disabled={isLoading}
        className={styles.button}
      >
        {isLoading ? 'Генерация...' : 'Заполнить данными'}
      </button>
      {feedbackMessage && <p className={styles.feedback}>{feedbackMessage}</p>}
    </div>
  );
};

export default DataSeeder; 