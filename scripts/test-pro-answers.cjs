#!/usr/bin/env node
/*
  Тест: проверка записи/чтения PRO-ответов
  Запуск: npm run test:pro
  Параметры (необязательно):
    API_BASE=https://hpi.expert:8443 DATE=2025-08-09 CATEGORY=problems SPHERE=1 TEXT="hello"
*/

const axios = require('axios');
const https = require('https');

const BASE_URL = process.env.API_BASE || 'https://hpi.expert:8443';
const CATEGORY = process.env.CATEGORY || 'problems';
const SPHERE = Number(process.env.SPHERE || '1');
const DATE = process.env.DATE || new Date().toISOString().slice(0, 10);
const TEXT = process.env.TEXT || `auto-test ${new Date().toISOString()}`;

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
  if (!data || !data.access_token) throw new Error('Не удалось получить access_token');
  return data.access_token;
}

async function postProAnswer(token) {
  const url = `${BASE_URL}/api/pro/answers/${CATEGORY}`;
  const payload = [{ sphere: String(SPHERE), text: TEXT, date: DATE }];
  const { data } = await axios.post(url, payload, {
    headers: { Authorization: `Bearer ${token}` },
    httpsAgent,
  });
  return data;
}

async function getProAnswers(token) {
  const url = `${BASE_URL}/api/pro/answers/${CATEGORY}`;
  const { data } = await axios.get(url, {
    params: { date: DATE },
    headers: { Authorization: `Bearer ${token}` },
    httpsAgent,
  });
  return data;
}

(async () => {
  try {
    console.log(`BASE_URL=${BASE_URL}`);
    console.log(`DATE=${DATE} CATEGORY=${CATEGORY} SPHERE=${SPHERE}`);

    const token = await getToken();
    console.log('Токен получен. Отправляю PRO-ответ...');
    await postProAnswer(token);
    console.log('POST OK. Читаю ответы...');

    const answers = await getProAnswers(token);
    const found = (answers || []).find(a => Number(a.sphere) === SPHERE && typeof a.text === 'string' && a.text.includes(TEXT.slice(0, 20)));
    if (found) {
      console.log('✅ Найден сохранённый ответ:', { id: found.id, sphere: found.sphere, text: found.text.slice(0, 60) });
      process.exit(0);
    } else {
      console.log('❌ Не найден сохранённый ответ. Ответы:', answers);
      process.exit(1);
    }
  } catch (e) {
    console.error('Ошибка теста:', e.response?.status, e.response?.data || e.message);
    process.exit(1);
  }
})(); 