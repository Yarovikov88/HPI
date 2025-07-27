import React from 'react';
// import type { Sphere } from '../services/api';
import styles from './ProQuestionForm.module.css';

interface SphereWithEmoji {
    id: string;
    name: string;
    emoji: string;
}

interface MetricDefinition {
    name: string;
    description: string;
}

interface MetricAnswer {
    current_value: number;
    target_value: number;
}

type ProMetricsFormProps = {
    sphere: SphereWithEmoji;
    metrics: MetricDefinition[];
    answers: Record<string, MetricAnswer>;
    onAnswerChange: (metricName: string, field: keyof MetricAnswer, value: number) => void;
};

const ProMetricsForm: React.FC<ProMetricsFormProps> = ({ sphere, metrics, answers, onAnswerChange }) => {
    return (
        <div className={styles.formContainer}>
            <h3 className={styles.sphereTitle}>{sphere.emoji} {sphere.name}</h3>
            {metrics.map((metric) => (
                <div key={metric.name} className={styles.metricRow}>
                    <p className={styles.metricDescription}>{metric.description}</p>
                    <div className={styles.metricInputs}>
                        <label>
                            Текущее значение:
                            <input
                                type="number"
                                value={answers[metric.name]?.current_value || ''}
                                onChange={(e) => onAnswerChange(metric.name, 'current_value', parseInt(e.target.value) || 0)}
                            />
                        </label>
                        <label>
                            Целевое значение:
                            <input
                                type="number"
                                value={answers[metric.name]?.target_value || ''}
                                onChange={(e) => onAnswerChange(metric.name, 'target_value', parseInt(e.target.value) || 0)}
                            />
                        </label>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default ProMetricsForm; 