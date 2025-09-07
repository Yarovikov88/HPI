import React from 'react';
import styles from './ProMetricsForm.module.css';

interface SphereWithEmoji {
    id: string;
    name: string;
    emoji: string;
}

interface MetricDefinition {
    name: string;
    unit: string;
    type: string;
}

interface ProMetricsFormProps {
    sphere: SphereWithEmoji;
    metrics: MetricDefinition[];
    answers: Record<string, any>;
    onAnswerChange: (metricName: string, field: string, value: any) => void;
    questionText?: string;
    showSphereTitle?: boolean;
}

const ProMetricsForm: React.FC<ProMetricsFormProps> = ({
  sphere,
  metrics,
  answers,
  onAnswerChange,
  questionText,
  showSphereTitle = true
}) => {
  // Получаем значение из ответов
  const getAnswerValue = () => {
    const answerKey = `metrics-${sphere.id}`;
    const answer = answers[answerKey];
    console.log('🔍 getAnswerValue:', { answerKey, answer });
    
    if (answer) {
      // Если есть text - проверяем что это
      if (answer.text && typeof answer.text === 'string') {
        const text: string = answer.text;
        // Парсим ТОЛЬКО если это похоже на JSON-объект
        const looksLikeJsonObject = text.trim().startsWith('{') && text.trim().endsWith('}');
        if (looksLikeJsonObject) {
          try {
            const parsed = JSON.parse(text);
            // Если это объект формата метрик, извлекаем what_measure
            if (parsed && typeof parsed === 'object' && 'what_measure' in parsed) {
              return parsed.what_measure || '';
            }
            // Иначе возвращаем исходный текст
            return text;
          } catch (e) {
            // Если не JSON, возвращаем как есть
            return text;
          }
        }
        // Обычная строка (включая числа, например "123")
        return text;
      }
      
      // Если есть старый формат с полями метрик
      if (metrics.length > 0 && answer[metrics[0].name]) {
        return answer[metrics[0].name].what_measure || '';
      }
    }
    return '';
  };

  // Обрабатываем изменение текста
  const handleTextChange = (value: string) => {
    console.log('🔍 handleTextChange:', { value });
    // Используем первое метрику для сохранения текста
    if (metrics.length > 0) {
      onAnswerChange(metrics[0].name, 'text', value);
    }
  };

  return (
    <div className={styles.container}>
      {/* Показываем эмодзи и название сферы при необходимости */}
      {showSphereTitle && (
        <h3 className={styles.sphereTitle}>
          <span className={styles.emoji}>{sphere.emoji}</span>
          {sphere.name}
        </h3>
      )}
      
      {/* Показываем текст вопроса из БД или имя метрики */}
      <h3 className={styles.questionTitle}>
        {questionText || (metrics[0]?.name || '')}
      </h3>
      
      {/* Один большой блок ввода без подсказки */}
      <div className={styles.singleInputContainer}>
        <textarea
          value={getAnswerValue()}
          onChange={(e) => handleTextChange(e.target.value)}
          placeholder={`Введите значение${metrics[0]?.unit ? ` (${metrics[0]?.unit})` : ''}`}
          className={styles.singleTextarea}
          rows={6}
        />
      </div>
    </div>
  );
};

export default ProMetricsForm; 