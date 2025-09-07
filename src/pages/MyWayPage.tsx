import React from 'react';
import Timeline from '../components/Timeline';
import { nodes as myWayNodes } from '../data/myWayNodes';
import styles from './MyWayPage.module.css';

const MyWayPage = () => {
  return (
    <div className={styles.pageContainer}>
      <header className={styles.pageHeader}>
        <h1>Мой путь</h1>
        <p>Интерактивная карта профессионального и жизненного развития</p>
      </header>
      <Timeline nodes={myWayNodes} />
    </div>
  );
};

export default MyWayPage; 