const express = require('express');
const multer = require('multer');
const path = require('path');
const axios = require('axios');
const cors = require('cors');
const FormData = require('form-data');
const https = require('https');
const http = require('http');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'dist')));

// Multer для загрузки файлов
const upload = multer({ 
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 5 * 1024 * 1024 // 5MB
  }
});

// Конфигурация
const BOT_TOKEN = process.env.CHANNEL_BOT_TOKEN || "8371425767:AAHE31OsvZSftj2YNxFa8oaSV7YShvdPk6w";
const ADMIN_CHAT_ID = process.env.ADMIN_CHAT_ID || "1014395380";

// Функция отправки в Telegram
async function sendToTelegram(text, photoBuffer = null) {
  try {
    if (photoBuffer) {
      const formData = new FormData();
      formData.append('chat_id', ADMIN_CHAT_ID);
      formData.append('caption', text);
      formData.append('photo', photoBuffer, { filename: 'feedback.jpg' });
      
      await axios.post(`https://api.telegram.org/bot${BOT_TOKEN}/sendPhoto`, formData, {
        headers: formData.getHeaders()
      });
    } else {
      await axios.post(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
        chat_id: ADMIN_CHAT_ID,
        text: text,
        parse_mode: 'HTML'
      });
    }
    return true;
  } catch (error) {
    console.error('Ошибка отправки в Telegram:', error);
    return false;
  }
}

// API для feedback
app.post('/api/feedback', upload.single('image'), async (req, res) => {
  try {
    const { type, message, user_id, user_email } = req.body;
    const image = req.file;

    console.log('Получен feedback:', { type, message, user_id, user_email, hasImage: !!image });

    const feedbackText = `
📝 <b>Новая обратная связь с сайта</b>

👤 <b>Пользователь:</b> ${user_email || 'Неизвестный'}
🆔 <b>User ID:</b> ${user_id || 'Неизвестный'}
📅 <b>Дата:</b> ${new Date().toLocaleString('ru-RU')}
🌐 <b>Страница:</b> ${req.headers.referer || 'Неизвестно'}
🔧 <b>Тип:</b> ${type === 'bug' ? '🐛 Ошибка' : '💡 Предложение'}

💬 <b>Сообщение:</b>
${message}

📱 <b>User Agent:</b>
${req.headers['user-agent'] || 'Неизвестно'}
    `.trim();

    let success = false;
    
    if (image) {
      success = await sendToTelegram(feedbackText, image.buffer);
    } else {
      success = await sendToTelegram(feedbackText);
    }

    if (success) {
      res.json({ success: true, message: 'Обратная связь отправлена' });
    } else {
      res.status(500).json({ success: false, message: 'Ошибка отправки' });
    }
  } catch (error) {
    console.error('Ошибка обработки feedback:', error);
    res.status(500).json({ success: false, message: 'Внутренняя ошибка сервера' });
  }
});

// Проксирование API запросов (кроме feedback)
app.use('/api', async (req, res) => {
  // Если это feedback, не проксируем
  if (req.path.includes('feedback')) {
    return; // Продолжаем обработку feedback
  }
  
  try {
    const response = await axios({
      method: req.method,
      url: `https://hpi.expert:8443${req.url}`,
      data: req.body,
      headers: {
        ...req.headers,
        host: 'hpi.expert:8443'
      },
      httpsAgent: new (require('https').Agent)({
        rejectUnauthorized: false
      })
    });
    
    res.status(response.status).json(response.data);
  } catch (error) {
    console.error('Ошибка проксирования API:', error);
    res.status(500).json({ error: 'Ошибка API' });
  }
});

// SPA fallback
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

// HTTPS сервер
const httpsOptions = {
  key: fs.readFileSync('/etc/letsencrypt/live/hpi.expert/privkey.pem'),
  cert: fs.readFileSync('/etc/letsencrypt/live/hpi.expert/fullchain.pem')
};

// HTTP сервер (для редиректа на HTTPS)
const httpApp = express();
httpApp.use((req, res) => {
  res.redirect(`https://${req.headers.host}${req.url}`);
});

// Запускаем оба сервера
http.createServer(httpApp).listen(80, () => {
  console.log('HTTP сервер запущен на порту 80 (редирект на HTTPS)');
});

https.createServer(httpsOptions, app).listen(443, () => {
  console.log('HTTPS сервер запущен на порту 443');
}); 