import React from 'react';
import { Outlet } from 'react-router-dom';
import SurveyProvider from '../contexts/SurveyContext';
import Sidebar from '../components/Sidebar';
import styles from './AccountLayout.module.css';

const ProtectedLayout = () => {
  return (
    <SurveyProvider>
      <div className={styles.accountLayout}>
        <Sidebar />
        <main className={styles.mainContent}>
          <Outlet />
        </main>
      </div>
    </SurveyProvider>
  );
};

export default ProtectedLayout; 