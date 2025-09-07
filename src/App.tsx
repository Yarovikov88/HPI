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
import ProSpherePage from './pages/ProSpherePage';
import DashboardPage from './pages/DashboardPage';
import ProDashboardPage from './pages/ProDashboardPage';
import HistoryPage from './pages/HistoryPage';
import CalendarPage from './pages/CalendarPage';
import { apiClient } from './services/api';
import TermsPage from './pages/TermsPage';
import PrivacyPage from './pages/PrivacyPage';
import CookiesPage from './pages/CookiesPage';
import RecommendationsPage from './pages/RecommendationsPage';
import ErrorBoundary from './components/ErrorBoundary';
import GetProPage from './pages/GetProPage';
import TestMetricsPage from './pages/TestMetricsPage';

function App() {
  // Убираем автологин через Telegram
  // useEffect(() => {
  //   const initAuth = async () => {
  //     const token = localStorage.getItem('authToken');
  //     if (!token) {
  //       await apiClient.telegramAuth();
  //     }
  //   };
  //   initAuth();
  // }, []);

  return (
    <HelmetProvider>
      <AuthProvider>
        <ScrollToTop />
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
            <Route path="terms" element={<TermsPage />} />
            <Route path="privacy" element={<PrivacyPage />} />
            <Route path="cookies" element={<CookiesPage />} />
            <Route path="recommendations" element={<RecommendationsPage />} />
            <Route path="test-metrics" element={<TestMetricsPage />} />

            {/* Protected Account Routes */}
            <Route 
              path="account"
              element={
                <SurveyProvider>
                  <AccountLayout />
                </SurveyProvider>
              }
            >
              <Route index element={<Navigate to="/account/profile" replace />} />
              <Route path="profile" element={<ProtectedRoute><AccountPage /></ProtectedRoute>} />
              <Route path="diagnostics" element={<ProtectedRoute><DiagnosticsPage /></ProtectedRoute>} />
              <Route path="get-pro" element={<ProtectedRoute><GetProPage /></ProtectedRoute>} />
              <Route path="survey" element={<ProtectedRoute><SurveyPage /></ProtectedRoute>} />
              <Route path="pro-survey" element={<ProtectedRoute pro><ProSurveyPage /></ProtectedRoute>} />
              <Route path="pro/problems" element={<ProtectedRoute pro><ProSurveyPage /></ProtectedRoute>} />
              <Route path="pro/goals" element={<ProtectedRoute pro><ProSurveyPage /></ProtectedRoute>} />
              <Route path="pro/blockers" element={<ProtectedRoute pro><ProSurveyPage /></ProtectedRoute>} />
              <Route path="pro/metrics" element={<ProtectedRoute pro><ProSurveyPage /></ProtectedRoute>} />
              <Route path="pro/achievements" element={<ProtectedRoute pro><ProSurveyPage /></ProtectedRoute>} />
              <Route path="pro/sphere/:sphereId" element={<ProtectedRoute pro><ProSpherePage /></ProtectedRoute>} />
              <Route path="dashboard" element={<ProtectedRoute><ErrorBoundary><DashboardPage /></ErrorBoundary></ProtectedRoute>} />
              <Route path="pro-dashboard" element={<ProtectedRoute pro><ProDashboardPage /></ProtectedRoute>} />
              <Route path="history" element={<ProtectedRoute><HistoryPage /></ProtectedRoute>} />
              <Route path="calendar" element={<ProtectedRoute><CalendarPage /></ProtectedRoute>} />
            </Route>
          </Route>
        </Routes>
      </AuthProvider>
    </HelmetProvider>
  );
}

export default App;
