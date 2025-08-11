#!/usr/bin/env node
/* basic_test.js — тест обычных вопросов с параметром date
   Запуск (PowerShell):
     $env:API_BASE='https://hpi.expert:8443'; $env:DATE='2025-08-07'; node basic_test.js
   ENV:
     API_BASE (default https://hpi.expert:8443)
     DATE (default today)
     USER_ID (default 1)
     SECRET (default 'your_secret_key')
     TOKEN (optional) — использовать готовый токен
     DO_POST ('1' to post before get)
*/

const axios = require('axios');
const https = require('https');
const crypto = require('crypto');

const API_BASE = process.env.API_BASE || 'https://hpi.expert:8443';
const DATE = process.env.DATE || new Date().toISOString().slice(0, 10);
const USER_ID = Number(process.env.USER_ID || '1');
const SECRET = process.env.SECRET || 'your_secret_key';
const DO_POST = process.env.DO_POST === '1';

const httpsAgent = process.env.ALLOW_INSECURE === '1'
  ? new https.Agent({ rejectUnauthorized: false })
  : undefined;

function b64url(s) { return Buffer.from(s).toString('base64').replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_'); }
function jwt(uid) {
  const h = b64url(JSON.stringify({ alg:'HS256', typ:'JWT' }));
  const p = b64url(JSON.stringify({ sub:String(uid) }));
  const d = `${h}.${p}`;
  const s = crypto.createHmac('sha256', SECRET).update(d).digest('base64').replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_');
  return `${d}.${s}`;
}

async function getBasic(date, token) {
  const url = `${API_BASE}/api/answers`;
  const { data } = await axios.get(url, { params:{ date }, headers:{ Authorization:`Bearer ${token}` }, httpsAgent });
  return data;
}

async function postBasic(date, token) {
  const url = `${API_BASE}/api/answers`;
  const body = [ { sphere:'1', question_id:'1.1', answer:3, date } ];
  const { data } = await axios.post(url, body, { headers:{ Authorization:`Bearer ${token}` }, httpsAgent });
  return data;
}

(async () => {
  try {
    const token = process.env.TOKEN || jwt(USER_ID);
    console.log(`API_BASE=${API_BASE} DATE=${DATE} USER_ID=${USER_ID}`);
    if (DO_POST) {
      const p = await postBasic(DATE, token);
      console.log('POST:', JSON.stringify(p, null, 2));
    }
    const g = await getBasic(DATE, token);
    console.log(`GET count: ${Array.isArray(g)? g.length:0}`);
    console.log('GET sample:', JSON.stringify((g||[]).slice(0,5), null, 2));
  } catch (e) {
    console.error('TEST ERROR:', e.response?.status, e.response?.data || e.message);
    process.exitCode = 1;
  }
})(); 