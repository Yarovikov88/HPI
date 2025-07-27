import { Outlet } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
import Header from './Header';
import Footer from './Footer';
import styles from '../App.module.css';

export default function Layout() {
  return (
    <AuthProvider>
      <Header />
      <main className={styles.mainContainer}>
        <Outlet />
      </main>
      <Footer />
    </AuthProvider>
  );
} 