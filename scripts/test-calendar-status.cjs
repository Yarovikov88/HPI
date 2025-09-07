#!/usr/bin/env node
/*
  Тестовый скрипт: проверка работы эндпоинта GET /api/calendar/status
  Запуск: npm run test:calendar
  Параметры (необязательно):
    API_BASE=https://hpi.expert:8443 FROM=2025-08-01 TO=2025-08-31 npm run test:calendar
*/

const axios = require('axios');
const https = require('https');

const BASE_URL = process.env.API_BASE || 'https://hpi.expert:8443';
const FROM = process.env.FROM || (() => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`;
})();
const TO = process.env.TO || (() => {
  const d = new Date();
  const last = new Date(d.getFullYear(), d.getMonth() + 1, 0);
  return `${last.getFullYear()}-${String(last.getMonth() + 1).padStart(2, '0')}-${String(last.getDate()).padStart(2, '0')}`;
})();

// Если у сервера самоподписанный сертификат, установите переменную окружения ALLOW_INSECURE=1
const httpsAgent = process.env.ALLOW_INSECURE === '1'
  ? new https.Agent({ rejectUnauthorized: false })
  : undefined;

async function getToken() {
  const authData = {
    id: 1014395380,
    first_name: 'WebApp',
    last_name: 'User',
    username: 'webappuser',
    photo_url: null,
  };
  const url = `${BASE_URL}/api/telegram_auth`;
  const { data } = await axios.post(url, authData, { httpsAgent });
  if (!data || !data.access_token) {
    throw new Error('Не удалось получить access_token');
  }
  return data.access_token;
}

async function getCalendarStatus(token, from, to) {
  const url = `${BASE_URL}/api/calendar/status`;
  const { data } = await axios.get(url, {
    params: { from, to },
    headers: { Authorization: `Bearer ${token}` },
    httpsAgent,
  });
  return data;
}

(async () => {
  try {
    console.log(`BASE_URL=${BASE_URL}`);
    console.log(`Диапазон: ${FROM} .. ${TO}`);

    const token = await getToken();
    console.log('Токен получен. Запрашиваю статусы...');

    const days = await getCalendarStatus(token, FROM, TO);
    console.log(`OK. Получено дней: ${Array.isArray(days) ? days.length : 0}`);

    // Краткое резюме по цветам календаря
    const summary = (days || []).reduce((acc, d) => {
      const basic = d?.basic?.status;
      const pro = d?.pro?.status;
      if (basic === 'complete' && pro === 'complete') acc.blue++;
      else if ((basic && basic !== 'none') || (pro && pro !== 'none')) acc.brown++;
      else acc.gray++;
      return acc;
    }, { blue: 0, brown: 0, gray: 0 });

    console.log('Сводка (календарь):', summary);
    console.log('Первые элементы:');
    console.log(JSON.stringify((days || []).slice(0, 5), null, 2));
  } catch (e) {
    console.error('Ошибка теста:', e.response?.status, e.response?.data || e.message);
    process.exitCode = 1;
  }
})(); 