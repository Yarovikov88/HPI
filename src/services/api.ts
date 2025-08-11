import axios, { AxiosError } from 'axios';
import { toast } from 'react-toastify';

// Типы для аутентификации и профиля
export interface UserLogin {
  email?: string;
  username?: string;
  password: string;
}

export interface UserRegister {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  username?: string;
  phone?: string;
}

export interface UserProfile {
  id: number | string;
  email?: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  phone?: string;
  telegram_id?: number;
  avatar_url?: string | null;
}

export type Question = any;

// Новые типы для ответов
export interface BasicAnswer {
  id: number;
  question_id: number;
  sphere: number;
  answer: string | number; // <- допускаем оба варианта
  date: string;
  created_at?: string;
}

export interface ProAnswer {
  id: number;
  sphere: number | string;
  text: string;
  date: string;
  category: string;
  created_at?: string;
}

// Новые типы для отправки данных (с поддержкой id для обновления)
export type BasicAnswerPayload = Omit<BasicAnswer, 'id'>;
export type ProAnswerPayload = {
  id?: number;
  sphere: number | string;
  text: string;
  date: string;
};


export type DashboardData = any;
export type RadarData = any;
export type TrendData = any;
export type Recommendation = any;
export type ProQuestion = any;

// Календарь: статусы на день
export type DayStatus = 'none' | 'draft' | 'complete';
export interface CalendarDayStatus {
  date: string; // YYYY-MM-DD
  basic: {
    status: DayStatus;
    answered?: number;
    total?: number;
  };
  pro: {
    status: DayStatus;
    answered?: number;
    total?: number;
  };
}

const PRO_CATEGORIES = ['problems', 'goals', 'blockers', 'metrics', 'achievements'];

const axiosInstance = axios.create({
  baseURL: '/api',
});

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      (config.headers as any).Authorization = `Bearer ${token}`;
    }
    // Always send JSON
    (config.headers as any)['Content-Type'] = 'application/json';
    return config;
  },
  (error) => Promise.reject(error)
);

axiosInstance.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Подавляем тост для 404 на DELETE /answers/{id}
    const status = (error.response as any)?.status as number | undefined;
    const method = (error.config as any)?.method;
    const url = (error.config as any)?.url as string | undefined;
    const isDeleteNotFoundOnAnswers = method === 'delete' && status === 404 && (url?.includes('/answers/'));

    if (!isDeleteNotFoundOnAnswers) {
      let errorMessage: string | undefined;

      // Попытка достать detail разных форматов
      const pickDetail = (data: any): string | undefined => {
        if (!data) return undefined;
        if (typeof data === 'string') return data;
        if (typeof data.detail === 'string') return data.detail;
        if (Array.isArray(data.detail) && data.detail.length > 0) {
          const first = data.detail[0];
          if (typeof first?.msg === 'string') return first.msg as string;
        }
        return undefined;
      };

      const responseData = (error.response as any)?.data as any;
      const detail = pickDetail(responseData);

      // Специальные дружелюбные сообщения
      if (status === 409 && (detail?.toLowerCase?.().includes('email') || detail === 'Email already in use')) {
        errorMessage = 'Этот email уже используется. Укажите другой адрес.';
      } else if (status === 422) {
        const d = (detail || '').toLowerCase();
        if (d.includes('phone') || d.includes('e.164')) {
          errorMessage = 'Телефон должен быть в международном формате +79990000000.';
        } else if (d.includes('email')) {
          errorMessage = 'Некорректный email. Проверьте формат.';
        }
      }

      if (!errorMessage) {
        if (detail) {
          errorMessage = detail;
        } else if (error.response) {
          errorMessage = `Ошибка: ${(error.response as any).status}`;
        } else if (error.request) {
          errorMessage = 'Не удалось подключиться к серверу.';
        } else {
          errorMessage = (error as any).message as string;
        }
      }

      toast.error(errorMessage);
    }

    return Promise.reject(error);
  }
);

export const apiClient = {
  // Auth
  telegramAuth: async () => {
    const authData = {
      id: 1014395380,
      first_name: 'VainBlade',
      last_name: 'VainBlade',
      username: 'VainBlade',
      photo_url: null,
    };
    try {
      const response = await axiosInstance.post('/telegram_auth', authData);
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
    // Если бэк вернёт токен при регистрации — сохраним
    const accessToken = (response.data as any)?.access_token;
    if (accessToken) {
      localStorage.setItem('authToken', accessToken);
    }
    return response.data;
  },
  login: async (data: UserLogin) => {
    const response = await axiosInstance.post('/auth/login', data);
    if ((response.data as any).access_token) {
      localStorage.setItem('authToken', (response.data as any).access_token);
    }
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('authToken');
  },

  // Profile
  getProfile: async (): Promise<UserProfile> => {
    const response = await axiosInstance.get('/profile');
    return response.data as UserProfile;
  },
  updateProfile: async (data: Partial<UserProfile>): Promise<UserProfile> => {
    // Нормализуем поля: full_name -> first_name/last_name, удаляем пустые строки
    const payload: Record<string, unknown> = {};
    const cleaned = Object.fromEntries(
      Object.entries(data).filter(([_, v]) => v !== undefined && v !== null && String(v).trim() !== '')
    ) as Partial<UserProfile> & { full_name?: string };

    if (cleaned.full_name && !cleaned.first_name && !cleaned.last_name) {
      const parts = cleaned.full_name.trim().split(/\s+/);
      const first = parts.shift() || '';
      const last = parts.join(' ');
      if (first) (payload as any).first_name = first;
      if (last) (payload as any).last_name = last;
    }
    if ((cleaned as any).first_name) (payload as any).first_name = (cleaned as any).first_name;
    if ((cleaned as any).last_name) (payload as any).last_name = (cleaned as any).last_name;
    if (cleaned.email) (payload as any).email = cleaned.email;
    if (cleaned.phone) (payload as any).phone = cleaned.phone;
    if (cleaned.username) (payload as any).username = cleaned.username;

    const response = await axiosInstance.put('/profile', payload);
    return response.data as UserProfile;
  },

  // Questions
  getQuestions: async (lang?: string): Promise<Question[]> => {
    const params = lang ? { lang } : undefined;
    const response = await axiosInstance.get('/questions', { params }); // согласно Swagger: GET /api/questions?lang=ru|en
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

  // Answers (Переработанные функции)

  /**
   * Получает базовые ответы за указанную дату.
   * @param date - Дата в формате 'YYYY-MM-DD'
   */
  getBasicAnswers: async (date: string): Promise<BasicAnswer[]> => {
    const response = await axiosInstance.get('/answers', {
      params: { date },
    });
    return response.data;
  },

  /**
   * Создает или обновляет базовый ответ (UPSERT).
   * @param payload - Данные ответа
   */
  upsertBasicAnswer: async (payload: BasicAnswerPayload): Promise<BasicAnswer> => {
    // Сервер ожидает массив с одним объектом, где id'шники - строки.
    const finalPayload = [{
      ...payload,
      question_id: String(payload.question_id),
      sphere: String(payload.sphere)
    }];
    
    console.debug('POST /answers with final payload:', finalPayload);
    const response = await axiosInstance.post('/answers', finalPayload);
    return response.data;
  },

  /**
   * Пакетное сохранение базовых ответов.
   * Сервер ожидает массив объектов, question_id и sphere — строки.
   */
  saveBasicAnswers: async (payloads: BasicAnswerPayload[]): Promise<BasicAnswer[]> => {
    const finalPayload = payloads.map(p => ({
      ...p,
      question_id: String(p.question_id),
      sphere: String(p.sphere),
    }));
    const response = await axiosInstance.post('/answers', finalPayload);
    return response.data;
  },

  /**
   * Удаляет базовый ответ по его ID.
   * @param answerId - ID ответа для удаления
   */
  deleteBasicAnswer: async (answerId: number): Promise<void> => {
    await axiosInstance.delete(`/answers/${answerId}`);
  },

  /**
   * Получает PRO ответы для указанной категории и даты.
   * @param category - Категория PRO-вопроса
   * @param date - Дата в формате 'YYYY-MM-DD'
   */
  getProAnswers: async (category: string, date: string): Promise<ProAnswer[]> => {
    const response = await axiosInstance.get(`/pro/answers/${category}`, {
      params: { date },
    });
    return response.data;
  },

  /**
   * Создает или обновляет PRO ответ (UPSERT одного элемента - совместимость)
   */
  upsertProAnswer: async (category: string, payload: ProAnswerPayload): Promise<ProAnswer> => {
    // Бэкенд ожидает список объектов, где числовые идентификаторы передаются строками
    const finalPayload = [{
      ...payload,
      sphere: String(payload.sphere),
    }];
    const response = await axiosInstance.post(`/pro/answers/${category}`, finalPayload);
    return response.data;
  },

  /**
   * Пакетное сохранение PRO ответов (список объектов).
   */
  saveProAnswers: async (category: string, payloads: ProAnswerPayload[]): Promise<ProAnswer[]> => {
    const finalPayload = payloads.map(p => ({
      ...p,
      sphere: String(p.sphere),
    }));
    const response = await axiosInstance.post(`/pro/answers/${category}`, finalPayload);
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
  
  // Calendar statuses by date range
  getCalendarStatus: async (from: string, to: string): Promise<CalendarDayStatus[]> => {
    // Ожидаемый эндпоинт на бэкенде: GET /api/calendar/status?from=YYYY-MM-DD&to=YYYY-MM-DD
    const response = await axiosInstance.get('/calendar/status', { params: { from, to } });
    return response.data;
  },
  
  // Debug
  seedScenario: async (userId: number, scenarioName: string): Promise<any> => {
    const payload = { user_id: userId, scenario_name: scenarioName };
    const response = await axiosInstance.post('/debug/seed-scenario/', payload);
    return response.data;
  },
}; 