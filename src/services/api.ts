import axios, { AxiosError } from 'axios';
import { toast } from 'react-toastify';

// Типы-заглушки
export type UserRegister = any;
export type UserLogin = any;
export type UserProfile = any;
export type Question = any;
export type AnswerPayload = any;
export type Answer = any;
export type DashboardData = any;
export type RadarData = any;
export type TrendData = any;
export type Recommendation = any;
export type ProQuestion = any;

const axiosInstance = axios.create({
  baseURL: "/api",
});

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

axiosInstance.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    let errorMessage = 'Произошла неизвестная ошибка.';
    if (error.response) {
      const responseData = error.response.data as any;
      errorMessage = responseData.detail || `Ошибка: ${error.response.status}`;
    } else if (error.request) {
      errorMessage = 'Не удалось подключиться к серверу.';
    } else {
      errorMessage = error.message;
    }
    toast.error(errorMessage);
    return Promise.reject(error);
  }
);

export const apiClient = {
  // Auth
  register: async (data: UserRegister) => {
    const response = await axiosInstance.post('/auth/register', data);
    return response.data;
  },
  login: async (data: UserLogin) => {
    const response = await axiosInstance.post('/auth/login', data);
    if (response.data.access_token) {
      localStorage.setItem('authToken', response.data.access_token);
    }
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('authToken');
  },

  // Profile
  getProfile: async (): Promise<UserProfile> => {
    const response = await axiosInstance.get('/profile/');
    return response.data;
  },
  updateProfile: async (data: UserProfile): Promise<UserProfile> => {
    const response = await axiosInstance.put('/profile/', data);
    return response.data;
  },

  // Questions
  getQuestions: async (): Promise<Question[]> => {
    const response = await axiosInstance.get('/questions/');
    return response.data;
  },
  getProQuestions: async (): Promise<ProQuestion[]> => {
    const response = await axiosInstance.get('/questions/pro/');
    return response.data;
  },

  // Answers
  submitAnswers: async (answers: AnswerPayload[]): Promise<Answer[]> => {
    const response = await axiosInstance.post('/answers/', answers);
    return response.data;
  },
  getAnswers: async (date?: string): Promise<Answer[]> => {
    const params = date ? { date_str: date } : {};
    const response = await axiosInstance.get('/answers/', { params });
    return response.data;
  },
  getProAnswers: async (date?: string): Promise<any[]> => {
    const params = date ? { date_str: date } : {};
    const response = await axiosInstance.get('/pro-answers/', { params });
    return response.data;
  },
  
  // Dashboard
  getDashboardData: async (date?: string): Promise<DashboardData> => {
    const params = date ? { date_str: date } : {};
    const response = await axiosInstance.get('/dashboard/', { params });
    return response.data;
  },
  getRadarData: async (date?: string): Promise<RadarData> => {
    const params = date ? { date_str: date } : {};
    const response = await axiosInstance.get('/dashboard/radar', { params });
    return response.data;
  },
  getTrendData: async (): Promise<TrendData> => {
    const response = await axiosInstance.get('/dashboard/trend');
    return response.data;
  },

  // Recommendations
  getRecommendations: async (date?: string): Promise<Recommendation[]> => {
    const params = date ? { date_str: date } : {};
    const response = await axiosInstance.get('/recommendations/', { params });
    return response.data;
  },
  getGeneralRecommendations: async (): Promise<Recommendation[]> => {
    const response = await axiosInstance.get('/recommendations/general');
    return response.data;
  },
  
  // Debug
  seedScenario: async (userId: number, scenarioName: string): Promise<any> => {
    const payload = { user_id: userId, scenario_name: scenarioName };
    const response = await axiosInstance.post('/debug/seed-scenario/', payload);
    return response.data;
  },
}; 