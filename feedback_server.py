from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging
import os
from dotenv import load_dotenv
import requests
from datetime import datetime

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для фронтенда

# Конфигурация - используем Channel Bot для отправки обратной связи
BOT_TOKEN = os.getenv("CHANNEL_BOT_TOKEN", "8371425767:AAHE31OsvZSftj2YNxFa8oaSV7YShvdPk6w")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "1014395380")  # Ваш Telegram ID

def send_telegram_message(chat_id: str, text: str, parse_mode: str = "HTML"):
    """Отправляет сообщение в Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Ошибка отправки в Telegram: {e}")
        return False

def send_telegram_photo(chat_id: str, photo_data, caption: str = ""):
    """Отправляет фото в Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        files = {"photo": ("image.jpg", photo_data, "image/jpeg")}
        data = {"chat_id": chat_id, "caption": caption}
        response = requests.post(url, files=files, data=data, timeout=30)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Ошибка отправки фото в Telegram: {e}")
        return False

@app.route('/feedback', methods=['POST'])
def handle_feedback():
    """Обрабатывает обратную связь с сайта"""
    logger.info(f"Получен запрос обратной связи от {request.remote_addr}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Form data: {dict(request.form)}")
    logger.info(f"Files: {list(request.files.keys())}")
    
    try:
        # Получаем данные из формы
        feedback_type = request.form.get('type', 'unknown')
        message = request.form.get('message', '')
        user_id = request.form.get('user_id', '')
        user_email = request.form.get('user_email', '')
        user_agent = request.form.get('userAgent', '')
        url = request.form.get('url', '')
        
        # Получаем фото, если есть
        photo = request.files.get('image')
        
        # Формируем сообщение для Telegram
        feedback_message = f"""
📝 <b>Новая обратная связь с сайта</b>

👤 <b>Пользователь:</b> {user_email or 'Неизвестный'}
🆔 <b>User ID:</b> {user_id}
📅 <b>Дата:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
🌐 <b>Страница:</b> {url}
🔧 <b>Тип:</b> {'🐛 Ошибка' if feedback_type == 'bug' else '💡 Предложение'}

💬 <b>Сообщение:</b>
{message}

📱 <b>User Agent:</b>
{user_agent}
        """.strip()
        
        # Отправляем текстовое сообщение
        success = send_telegram_message(ADMIN_CHAT_ID, feedback_message)
        
        # Отправляем фото, если есть
        if photo and success:
            photo_caption = f"📸 Фото от пользователя {user_email} (User ID: {user_id})"
            send_telegram_photo(ADMIN_CHAT_ID, photo.read(), photo_caption)
        
        if success:
            logger.info(f"Обратная связь успешно отправлена от пользователя {user_email}")
            return jsonify({"success": True, "message": "Обратная связь отправлена"}), 200
        else:
            logger.error("Не удалось отправить обратную связь в Telegram")
            return jsonify({"success": False, "message": "Ошибка отправки"}), 500
            
    except Exception as e:
        logger.error(f"Ошибка обработки обратной связи: {e}")
        return jsonify({"success": False, "message": "Внутренняя ошибка сервера"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()}), 200

if __name__ == '__main__':
    logger.info("Feedback server запущен")
    # В Docker используем 0.0.0.0 для доступа извне контейнера
    app.run(host='0.0.0.0', port=5001, debug=False) 