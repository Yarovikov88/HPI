import React from 'react';
import styles from './ProQuestionForm.module.css';

interface ProQuestionFormProps {
  sphere: { id: string; name: string; emoji: string };
  answer: string;
  onAnswerChange: (answer: string) => void;
  readOnly?: boolean;
}

const ProQuestionForm: React.FC<ProQuestionFormProps> = ({
  sphere,
  answer,
  onAnswerChange,
  readOnly = false,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (!readOnly) onAnswerChange(e.target.value);
  };

  return (
    <div className={styles.formContainer}>
      <h3 className={styles.sphereTitle}>
        <span className={styles.emoji}>{sphere.emoji}</span>
        {sphere.name}
      </h3>
      <textarea
        id={sphere.id}
        value={answer}
        onChange={handleChange}
        className={styles.textareaInput}
        placeholder={readOnly ? '' : 'Опишите здесь...'}
        rows={5}
        readOnly={readOnly}
      />
    </div>
  );
};

export default ProQuestionForm; 