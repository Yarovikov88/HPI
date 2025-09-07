import { Outlet } from 'react-router-dom';
import Header from './Header';
import Footer from './Footer';
import styles from '../App.module.css';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useAuth } from '../hooks/useAuth';

export default function Layout() {
  const { isAuthenticated } = useAuth();

  return (
    <div className={styles.layout}>
      <Header />
      <main className={styles.mainContainer}>
        <Outlet />
      </main>
      {!isAuthenticated && <Footer />}
      <ToastContainer position="top-right" autoClose={2500} hideProgressBar={false} newestOnTop={false} closeOnClick pauseOnFocusLoss draggable pauseOnHover />
    </div>
  );
} 