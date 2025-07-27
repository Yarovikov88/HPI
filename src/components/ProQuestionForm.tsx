import React from 'react';
import styles from './ProQuestionForm.module.css';

interface ProQuestionFormProps {
  sphere: { id: string; name: string; emoji: string };
  questionId: string;
  answer: string;
  onAnswerChange: (questionId: string, answer: string) => void;
}

const ProQuestionForm: React.FC<ProQuestionFormProps> = ({
  sphere,
  questionId,
  answer,
  onAnswerChange,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onAnswerChange(questionId, e.target.value);
  };

  return (
    <div className={styles.formContainer}>
      <h3 className={styles.sphereTitle}>
        <span className={styles.emoji}>{sphere.emoji}</span>
        {sphere.name}
      </h3>
      <textarea
        id={questionId}
        value={answer}
        onChange={handleChange}
        className={styles.textareaInput}
        placeholder="Опишите здесь..."
        rows={5}
      />
    </div>
  );
};

export default ProQuestionForm; 