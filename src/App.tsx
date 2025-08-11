import { useEffect } from 'react';
import { Routes, Route, Navigate } from "react-router-dom";
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider } from './contexts/AuthContext';
import SurveyProvider from "./contexts/SurveyContext";

import ScrollToTop from "./components/ScrollToTop";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";

// Pages
import Home from './Home';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import MethodologyPage from './pages/MethodologyPage';
import FeaturesPage from './pages/FeaturesPage';
import PricingPage from './pages/PricingPage';
import DashboardFeaturePage from './pages/features/DashboardFeaturePage';
import AiFeaturePage from './pages/features/AiFeaturePage';
import GoalsFeaturePage from './pages/features/GoalsFeaturePage';
import BusinessPage from './pages/BusinessPage';
import IntegrationsPage from './pages/IntegrationsPage';

// Account Pages
import AccountLayout from './pages/AccountLayout';
import AccountPage from './pages/AccountPage';
import DiagnosticsPage from './pages/DiagnosticsPage';
import SurveyPage from './pages/SurveyPage';
import ProSurveyPage from './pages/ProSurveyPage';
import DashboardPage from './pages/DashboardPage';
import ProDashboardPage from './pages/ProDashboardPage';
import HistoryPage from './pages/HistoryPage';
import { apiClient } from './services/api';

function App() {
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('authToken');
      if (!token) {
        await apiClient.telegramAuth();
      }
    };
    initAuth();
  }, []);

  return (
              <Routes>
                <Route path="/" element={<Layout />}>
                  {/* Public routes */}
                  <Route index element={<Home />} />
                  <Route path="login" element={<LoginPage />} />
                  <Route path="signup" element={<SignupPage />} />
                  <Route path="methodology" element={<MethodologyPage />} />
                  <Route path="features" element={<FeaturesPage />} />
        <Route path="pricing" element={<PricingPage />} />
        <Route path="features/dashboard" element={<DashboardFeaturePage />} />
        <Route path="features/ai" element={<AiFeaturePage />} />
        <Route path="features/ai-recommendations" element={<AiFeaturePage />} />
        <Route path="features/goals" element={<GoalsFeaturePage />} />
        <Route path="business" element={<BusinessPage />} />
        <Route path="integrations" element={<IntegrationsPage />} />

                  {/* Protected Account Routes */}
                  <Route 
                    path="account" 
                    element={<ProtectedRoute><AccountLayout /></ProtectedRoute>}
                  >
                    <Route index element={<Navigate to="/account/profile" replace />} />
                    <Route path="profile" element={<AccountPage />} />
                    <Route path="diagnostics" element={<DiagnosticsPage />} />
                    <Route path="survey" element={<SurveyPage />} />
                    <Route path="pro-survey" element={<ProSurveyPage />} />
                    <Route path="pro/:category" element={<ProSurveyPage />} />
                    <Route path="dashboard" element={<DashboardPage />} />
                    <Route path="pro-dashboard" element={<ProDashboardPage />} />
                    <Route path="history" element={<HistoryPage />} />
                  </Route>
                </Route>
              </Routes>
  );
}

export default App;
