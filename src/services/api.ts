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
	has_password?: boolean;
    is_pro?: boolean;
}

export type Question = any;

// Новые типы для ответов
export interface BasicAnswer {
	id: number;
	question_id: string; // Исправляем: сервер ожидает строку
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
	// Дополнительные поля для метрик
	what_measure?: string;
	target_value?: number;
	unit?: string;
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
export type Recommendation = { title?: string; name?: string; text?: string; description?: string; suggestion?: string };
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

// Новый тип для объединенного дашборда
export interface CombinedDashboardData {
	hpi: number;
	sphere_scores: Record<string, number>;
	trend: Array<{ date: string; hpi: number }>;
	date: string | null;
	month: string | null;
	performance?: {
		execution_time_ms: number;
		cached: boolean;
	};
	error?: string;
}

const PRO_CATEGORIES = ['problems', 'goals', 'blockers', 'metrics', 'achievements'];

const axiosInstance = axios.create({
	baseURL: (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_API_BASE) || '/api',
	timeout: 30000, // Увеличиваем таймаут до 30 секунд
});

// Throttle for repetitive error toasts
const toastCooldownMs = 15000; // 15s
const lastToastAtByMessage: Record<string, number> = {};
const shouldShowToast = (message: string) => {
	const now = Date.now();
	const last = lastToastAtByMessage[message] || 0;
	if (now - last < toastCooldownMs) return false;
	lastToastAtByMessage[message] = now;
	return true;
};

axiosInstance.interceptors.request.use(
	(config) => {
		const token = localStorage.getItem('authToken');
		if (token) {
			(config.headers as any).Authorization = `Bearer ${token}`;
		}
		// Не шлём токен на неавторизованные эндпоинты (новые и легаси)
		const url = String(config.url || '');
		if (
			url.includes('/login') || url.includes('/register') || url.includes('/telegram_auth') ||
			url === '/login' || url === '/register' || url.includes('/login?') || url.includes('/register?')
		) {
			delete (config.headers as any).Authorization;
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
		const isGetRecommendations404 = method === 'get' && status === 404 && !!url && url.includes('/recommendations');
		const isAiGenerate500 = method === 'post' && status === 500 && !!url && url.includes('/recommendations/ai/generate');

		// Если пользователь уже вышел (токена нет), не показываем тосты об 401
		const noToken = !localStorage.getItem('authToken');

		if (!isDeleteNotFoundOnAnswers) {
			// Тихо пропускаем 500 на POST /recommendations/ai/generate — дадим верхнему уровню упасть в фолбэки
			if (isAiGenerate500) {
				return Promise.reject(error);
			}
			let errorMessage: string | undefined;

			// Попытка достать detail разных форматов
			const pickDetail = (data: any): string | undefined => {
				if (!data) return undefined;
				if (typeof data === 'string') return data;
				if (typeof (data as any).detail === 'string') return (data as any).detail;
				if (Array.isArray((data as any).detail) && (data as any).detail.length > 0) {
					const first = (data as any).detail[0];
					if (typeof first?.msg === 'string') return first.msg as string;
				}
				return undefined;
			};

			const responseData = (error.response as any)?.data as any;
			const detail = pickDetail(responseData);
			const rawText = (() => {
				try {
					if (typeof responseData === 'string') return responseData;
					if (responseData) return JSON.stringify(responseData);
				} catch {}
				return '';
			})().toLowerCase();

			// Тихо игнорируем 404 на GET /recommendations* — просто нет данных
			if (isGetRecommendations404) {
				return Promise.resolve({ data: [] } as any);
			}

			// Тихо игнорируем 401/"not authenticated" если токена нет (выход/истёкшая сессия)
			const looksUnauthorized = status === 401 || rawText.includes('not authenticated') || (detail || '').toLowerCase().includes('not authenticated');
			if (looksUnauthorized && noToken) {
				return Promise.reject(error);
			}

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

			// Бэкенд может вернуть 500 при нарушении уникальности — распознаём по текстам БД
			const looksLikeDuplicateEmail =
				rawText.includes('duplicate key') ||
				rawText.includes('unique constraint') ||
				rawText.includes('violates unique constraint') ||
				rawText.includes('unique') && rawText.includes('email') ||
				(detail || '').toLowerCase().includes('email already in use');

			if (!errorMessage && (status === 500 || status === 400) && looksLikeDuplicateEmail) {
				errorMessage = 'Этот email уже используется. Укажите другой адрес.';
			}

			// Показываем тост только если есть сообщение и прошло достаточно времени
			if (errorMessage && shouldShowToast(errorMessage)) {
				toast.error(errorMessage);
			}
		}

		return Promise.reject(error);
	}
);

// Кэш для API запросов
const apiCache = new Map<string, { data: any; timestamp: number; ttl: number }>();

const getCachedData = (key: string) => {
	const cached = apiCache.get(key);
	if (cached && Date.now() - cached.timestamp < cached.ttl) {
		return cached.data;
	}
	return null;
};

const setCachedData = (key: string, data: any, ttl: number = 300000) => {
	apiCache.set(key, { data, timestamp: Date.now(), ttl });
};

// Функция для очистки устаревшего кэша
const cleanupCache = () => {
	const now = Date.now();
	for (const [key, cached] of apiCache.entries()) {
		if (now - cached.timestamp > cached.ttl) {
			apiCache.delete(key);
		}
	}
};

// Запускаем очистку кэша каждые 5 минут
setInterval(cleanupCache, 300000);

export const apiClient = {
	// Аутентификация
	login: async (credentials: UserLogin) => {
		const response = await axiosInstance.post('/login', credentials);
		
		// Сохраняем токен в localStorage
		if (response.data.access_token) {
			localStorage.setItem('authToken', response.data.access_token);
		}
		
		return response.data;
	},

	register: async (userData: UserRegister) => {
		const response = await axiosInstance.post('/register', userData);
		
		// Сохраняем токен в localStorage если он есть
		if (response.data.access_token) {
			localStorage.setItem('authToken', response.data.access_token);
		}
		
		return response.data;
	},

	logout: () => {
		// Удаляем токен из localStorage
		localStorage.removeItem('authToken');
	},

	changePassword: async (data: { old_password?: string; new_password: string }) => {
		const response = await axiosInstance.put('/password', data);
		return response.data;
	},

	// Вопросы
	getBasicQuestions: async (lang?: string) => {
		console.log('getBasicQuestions called with lang:', lang);
		const cacheKey = `questions:${lang || 'ru'}`;
		const cached = getCachedData(cacheKey);
		if (cached) {
			console.log('Returning cached data:', cached);
			return cached;
		}

		console.log('Making API request to /questions');
		const response = await axiosInstance.get('/questions', { params: { lang } });
		console.log('API response:', response.data);
		setCachedData(cacheKey, response.data, 600000); // 10 минут
		return response.data;
	},

	// Алиас для совместимости
	getQuestions: async (lang?: string) => {
		console.log('getQuestions called with lang:', lang);
		const result = await apiClient.getBasicQuestions(lang);
		console.log('getQuestions result:', result);
		return result;
	},

	// Ответы
	postBasicAnswers: async (answers: BasicAnswerPayload[]) => {
		const response = await axiosInstance.post('/answers', answers);
		// Инвалидируем кэш дашборда
		apiCache.forEach((_, key) => {
			if (key.includes('dashboard') || key.includes('trend') || key.includes('radar')) {
				apiCache.delete(key);
			}
		});
		return response.data;
	},

	getBasicAnswers: async (date: string) => {
		const response = await axiosInstance.get('/answers', { params: { date } });
		return response.data;
	},

	deleteAnswer: async (id: number) => {
		try {
			await axiosInstance.delete(`/answers/${id}`);
			// Инвалидируем кэш дашборда
			apiCache.forEach((_, key) => {
				if (key.includes('dashboard') || key.includes('trend') || key.includes('radar')) {
					apiCache.delete(key);
				}
			});
			return true;
		} catch (error) {
			return false;
		}
	},

	// Дашборд - объединенный запрос для оптимизации
	getCombinedDashboard: async (date?: string): Promise<CombinedDashboardData> => {
		const response = await axiosInstance.get('/dashboard/combined', { params: { date } });
		return response.data;
	},

	// Отдельные эндпоинты для совместимости
	getDashboard: async (date?: string) => {
		const response = await axiosInstance.get('/dashboard', { params: { date } });
		return response.data;
	},

	getRadar: async (date?: string) => {
		const response = await axiosInstance.get('/radar', { params: { date } });
		return response.data;
	},

	getTrend: async (month?: string, date?: string) => {
		const response = await axiosInstance.get('/trend', { params: { month, date } });
		return response.data;
	},

	getSphereTrend: async (sphere: string, month?: string, date?: string) => {
		const response = await axiosInstance.get(`/spheres/trend`, { params: { sphere, month, date } });
		return response.data;
	},

	// PRO функции
	getProQuestions: async (category: string, lang?: string) => {
		const cacheKey = `pro_questions:${category}:${lang || 'ru'}`;
		const cached = getCachedData(cacheKey);
		if (cached) return cached;

		const response = await axiosInstance.get(`/pro/questions/${category}`, { params: { lang } });
		setCachedData(cacheKey, response.data, 600000); // 10 минут
		return response.data;
	},

	getProAnswers: async (category: string, date: string): Promise<ProAnswer[]> => {
		try {
			const response = await axiosInstance.get(`/pro/answers/${category}?date=${date}`);
			return response.data;
		} catch (error) {
			console.error(`Failed to get PRO answers for ${category}:`, error);
			return [];
		}
	},

	getProCompletionStatus: async (date: string): Promise<any> => {
		try {
			const response = await axiosInstance.get(`/pro/completion-status?date=${date}`);
			return response.data;
		} catch (error) {
			console.error('Failed to get PRO completion status:', error);
			return {
				overall_complete: false,
				spheres: {},
				total_spheres: 8,
				completed_spheres: 0
			};
		}
	},

	postProAnswer: async (category: string, data: ProAnswerPayload) => {
		// Backend expects a list of ProAnswer items in the body
		const payloadArray = [
			{
				sphere: Number((data as any).sphere),
				text: (data as any).text,
				date: (data as any).date,
			},
		];
		const response = await axiosInstance.post(`/pro/answers/${category}`, payloadArray);
		// Инвалидируем кэш дашборда
		apiCache.forEach((_, key) => {
			if (key.includes('dashboard') || key.includes('trend') || key.includes('radar')) {
				apiCache.delete(key);
			}
		});
		return response.data;
	},

	deleteProAnswer: async (category: string, id: number) => {
		try {
			await axiosInstance.delete(`/pro/answers/${category}/${id}`);
			// Инвалидируем кэш дашборда
			apiCache.forEach((_, key) => {
				if (key.includes('dashboard') || key.includes('trend') || key.includes('radar')) {
					apiCache.delete(key);
				}
			});
			return true;
		} catch (error) {
			return false;
		}
	},

	// Рекомендации
	getRecommendations: async (date?: string) => {
		// Сначала пробуем получить AI рекомендации
		try {
			console.log('🤖 Запрашиваем AI рекомендации для даты:', date);
			const aiResponse = await axiosInstance.get('/recommendations/ai', { params: { date } });
			console.log('🤖 AI рекомендации получены:', aiResponse.data);
			
			if (aiResponse.data.ai_recommendations && aiResponse.data.ai_recommendations.length > 0) {
				return aiResponse.data.ai_recommendations;
			}
		} catch (error) {
			console.log('🤖 AI рекомендации недоступны, пробуем базовые:', error);
		}

		// Если AI рекомендаций нет, пробуем базовые
		try {
			console.log('📋 Запрашиваем базовые рекомендации для даты:', date);
			const response = await axiosInstance.get('/recommendations', { params: { date } });
			console.log('📋 Базовые рекомендации получены:', response.data);
			return response.data;
		} catch (error) {
			console.error('❌ Ошибка загрузки рекомендаций:', error);
			return [];
		}
	},

	generateAiRecommendations: async (date?: string) => {
		try {
			console.log('🚀 Генерируем AI рекомендации для даты:', date);
			const response = await axiosInstance.post('/recommendations/ai/generate', undefined, { 
				params: { date, save: true } 
			});
			console.log('✅ AI рекомендации сгенерированы:', response.data);
			
			// Очищаем кэш после генерации
			const cacheKey = `recommendations:${date || 'latest'}`;
			apiCache.delete(cacheKey);
			console.log('🗑️ Кэш очищен для ключа:', cacheKey);
			
			return response.data;
		} catch (error) {
			console.error('❌ Ошибка генерации AI рекомендаций:', error);
			return [];
		}
	},

	// Календарь
	getCalendarStatus: async (from: string, to: string) => {
		// Всегда запрашиваем актуальные статусы без кэша, чтобы календарь отражал свежие данные
		const response = await axiosInstance.get('/calendar/status', { params: { from, to } });
		return response.data;
	},

	// Профиль
	getProfile: async () => {
		const cacheKey = 'profile';
		const cached = getCachedData(cacheKey);
		if (cached) return cached;

		const response = await axiosInstance.get('/profile');
		setCachedData(cacheKey, response.data, 600000); // 10 минут
		return response.data;
	},

	updateProfile: async (data: Partial<UserProfile>) => {
		const response = await axiosInstance.put('/profile', data);
		// Инвалидируем кэш профиля
		apiCache.delete('profile');
		return response.data;
	},

	// Telegram
	telegramAuth: async () => {
		const response = await axiosInstance.get('/telegram_auth');
		return response.data;
	},

	// Утилиты
	clearCache: () => {
		apiCache.clear();
	},

	invalidateCache: (pattern: string) => {
		apiCache.forEach((_, key) => {
			if (key.includes(pattern)) {
				apiCache.delete(key);
			}
		});
	}
}; 