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

const PRO_CATEGORIES = ['problems', 'goals', 'blockers', 'metrics', 'achievements'];

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
  telegramAuth: async () => {
    const authData = {
      id: 1014395380,
      first_name: "WebApp",
      last_name: "User",
      username: "webappuser",
      photo_url: null,
    };
    try {
      // Используем относительный путь, чтобы сработал прокси
      const response = await axios.post('/api/telegram_auth', authData);
      if (response.data.access_token) {
        localStorage.setItem('authToken', response.data.access_token);
        console.log("Токен получен и сохранен!");
        return response.data.access_token;
      }
    } catch (error) {
      console.error("Ошибка при получении токена:", error);
      toast.error("Не удалось автоматически авторизоваться.");
    }
    return null;
  },
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
    const response = await axiosInstance.get('/questions'); // ИСПРАВЛЕНО СОГЛАСНО SWAGGER
    return response.data;
  },
  getProQuestions: async (): Promise<ProQuestion[]> => {
    const requests = PRO_CATEGORIES.map(category =>
      axiosInstance.get(`/pro/questions/${category}`)
    );
    const responses = await Promise.all(requests);
    
    let allProQuestions: ProQuestion[] = [];
    responses.forEach((response, index) => {
        const category = PRO_CATEGORIES[index];
        const questions = response.data.map((q: any) => ({
            ...q,
            category,
            sphere_id: q.sphere // <--- ДОБАВЛЯЕМ ЭТУ СТРОКУ
        }));
        allProQuestions = [...allProQuestions, ...questions];
    });
    return allProQuestions;
  },

  // Answers
  submitAnswers: async (answers: AnswerPayload[]): Promise<Answer[]> => {
    const response = await axiosInstance.post('/answers', answers); // ИСПРАВЛЕНО СОГЛАСНО SWAGGER
    return response.data;
  },
  getAnswers: async (date?: string): Promise<Answer[]> => {
    const params = date ? { date_str: date } : {};
    const response = await axiosInstance.get('/answers', { params }); // ИСПРАВЛЕНО СОГЛАСНО SWAGGER
    return response.data;
  },
  getProAnswers: async (date?: string): Promise<any[]> => {
    // date is not used here based on swagger, but kept for consistency
    const requests = PRO_CATEGORIES.map(category =>
        axiosInstance.get(`/pro/answers/${category}`)
      );
    const responses = await Promise.all(requests);
    return responses.flatMap(response => response.data);
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