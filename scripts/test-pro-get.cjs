#!/usr/bin/env node
/*
  Тест: проверка нового эндпоинта GET /api/pro/answers/{category}?date=YYYY-MM-DD
  Запуск:
    npm run test:pro:get
  Параметры (опционально):
    API_BASE=https://hpi.expert:8443 DATE=2025-08-06 CATEGORY=problems npm run test:pro:get
    USER_ID=1 SECRET=myjwtsecret VERIFY=1 npm run test:pro:get
*/

const axios = require('axios');
const https = require('https');
const crypto = require('crypto');
const { Client } = require('pg');

const BASE_URL = process.env.API_BASE || 'https://hpi.expert:8443';
const CATEGORY = process.env.CATEGORY || 'problems';
const DATE = process.env.DATE || new Date().toISOString().slice(0, 10);
const USER_ID = Number(process.env.USER_ID || '1');
const SECRET = process.env.SECRET || 'your_secret_key';
const VERIFY = process.env.VERIFY === '1';

const httpsAgent = process.env.ALLOW_INSECURE === '1'
  ? new https.Agent({ rejectUnauthorized: false })
  : undefined;

// DB config (ENV можно переопределить при необходимости)
const DB_HOST = process.env.DB_HOST || '83.147.192.188';
const DB_PORT = Number(process.env.DB_PORT || '5433');
const DB_NAME = process.env.DB_NAME || 'hpi_db';
const DB_USER = process.env.DB_USER || 'hpi_user';
const DB_PASSWORD = process.env.DB_PASSWORD || 'hpi_password_2024';

function base64urlEncode(input) {
  return Buffer.from(input).toString('base64').replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
}

function base64urlDecode(input) {
  const b64 = input.replace(/-/g, '+').replace(/_/g, '/');
  return Buffer.from(b64, 'base64').toString('utf8');
}

function createJwtForUser(userId) {
  const header = { alg: 'HS256', typ: 'JWT' };
  const payload = { sub: String(userId) };
  const encodedHeader = base64urlEncode(JSON.stringify(header));
  const encodedPayload = base64urlEncode(JSON.stringify(payload));
  const data = `${encodedHeader}.${encodedPayload}`;
  const signature = crypto
    .createHmac('sha256', SECRET)
    .update(data)
    .digest('base64')
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');
  return `${data}.${signature}`;
}

async function getToken() {
  // Используем локальный JWT для указанного USER_ID
  return createJwtForUser(USER_ID);
}

function decodeUserIdFromJwt(token) {
  try {
    const [, payloadB64] = token.split('.');
    const json = base64urlDecode(payloadB64);
    const payload = JSON.parse(json);
    return payload?.sub ? Number(payload.sub) : undefined;
  } catch (_) {
    return undefined;
  }
}

async function getProfile(token) {
  const url = `${BASE_URL}/api/profile`;
  const { data } = await axios.get(url, {
    headers: { Authorization: `Bearer ${token}` },
    httpsAgent,
  });
  return data;
}

async function getCalendarStatus(token) {
  const url = `${BASE_URL}/api/calendar/status`;
  const { data } = await axios.get(url, {
    params: { from: process.env.FROM || DATE, to: process.env.TO || DATE },
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

async function getDbProAnswers(userId) {
  const client = new Client({ host: DB_HOST, port: DB_PORT, database: DB_NAME, user: DB_USER, password: DB_PASSWORD });
  await client.connect();
  const params = [userId, DATE];
  let sql;
  if (CATEGORY === 'metrics') {
    sql = `
      SELECT DISTINCT ON (user_id, date, sphere, name)
        id, user_id, date, 'metrics' AS category, sphere, name AS text, created_at
      FROM metrics
      WHERE user_id = $1 AND date = $2
      ORDER BY user_id, date, sphere, name, id DESC
    `;
  } else if (CATEGORY === 'achievements') {
    sql = `
      SELECT DISTINCT ON (user_id, date, sphere)
        id, user_id, date, 'achievements' AS category, sphere, description AS text, created_at
      FROM achievements
      WHERE user_id = $1 AND date = $2
      ORDER BY user_id, date, sphere, id DESC
    `;
  } else {
    sql = `
      SELECT DISTINCT ON (user_id, date, sphere)
        id, user_id, date, '${CATEGORY}' AS category, sphere, text AS text, created_at
      FROM ${CATEGORY}
      WHERE user_id = $1 AND date = $2
      ORDER BY user_id, date, sphere, id DESC
    `;
  }
  const { rows } = await client.query(sql, params);
  await client.end();
  return rows;
}

function toKey(row) {
  if (CATEGORY === 'metrics') return `${row.sphere}::${row.text}`; // text=metric name
  return String(row.sphere);
}

function compareApiDb(apiRows, dbRows) {
  const apiMap = new Map(apiRows.map(r => [toKey(r), r.id]));
  const dbMap = new Map(dbRows.map(r => [toKey(r), r.id]));
  const keys = new Set([...apiMap.keys(), ...dbMap.keys()]);
  const diffs = [];
  for (const k of keys) {
    if (apiMap.get(k) !== dbMap.get(k)) {
      diffs.push({ key: k, id_api: apiMap.get(k), id_db: dbMap.get(k) });
    }
  }
  return diffs;
}

(async () => {
  try {
    console.log(`BASE_URL=${BASE_URL}`);
    console.log(`CATEGORY=${CATEGORY} DATE=${DATE} USER_ID=${USER_ID}`);

    const token = await getToken();

    const userIdFromJwt = decodeUserIdFromJwt(token);
    if (userIdFromJwt !== undefined) {
      console.log(`user_id(jwt)=${userIdFromJwt}`);
    }

    try {
      const profile = await getProfile(token);
      console.log(`user_id(api)=${profile?.user_id}`);
    } catch (e) {
      console.log('user_id(api): не удалось получить профиль');
    }

    try {
      const cal = await getCalendarStatus(token);
      const day = Array.isArray(cal) ? cal[0] : null;
      console.log('calendar/status:', JSON.stringify(day || cal, null, 2));
    } catch (e) {
      console.log('calendar/status: ошибка', e.response?.status, e.response?.data || e.message);
    }

    console.log('Токен получен. Запрашиваю ответы (API)...');

    let apiItems;
    try {
      apiItems = await getProAnswers(token);
      console.log(`API OK. Получено записей: ${Array.isArray(apiItems) ? apiItems.length : 0}`);
    } catch (e) {
      console.log('API ошибка:', e.response?.status, e.response?.data || e.message);
    }

    const dbRows = await getDbProAnswers(USER_ID);
    console.log(`DB OK. Найдено строк: ${dbRows.length}`);

    if (VERIFY && Array.isArray(apiItems)) {
      const diffs = compareApiDb(apiItems, dbRows);
      if (diffs.length) {
        console.log('Расхождения API vs DB:', JSON.stringify(diffs, null, 2));
        process.exitCode = 1;
      } else {
        console.log('Верификация OK: API совпадает с DB по id последней строки на ключ.');
      }
    }

    if (!apiItems || !Array.isArray(apiItems) || apiItems.length === 0) {
      console.log('Первые элементы (DB):');
      console.log(JSON.stringify(dbRows.slice(0, 5), null, 2));
    } else {
      console.log('Первые элементы (API):');
      console.log(JSON.stringify(apiItems.slice(0, 5), null, 2));
    }
  } catch (e) {
    console.error('Ошибка теста:', e.response?.status, e.response?.data || e.message);
    process.exitCode = 1;
  }
})(); 