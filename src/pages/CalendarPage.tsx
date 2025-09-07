import React from 'react';
import { CalendarWidget } from '../components/CalendarWidget';
import styles from './CalendarPage.module.css';

const CalendarPage: React.FC = () => {
  return (
    <div className={styles.calendarPage}>
      <h1 className={styles.title}>История</h1>
      <CalendarWidget />
    </div>
  );
};

export default CalendarPage; 