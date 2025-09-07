#!/usr/bin/env python3
"""
Скрипт для запуска сервера обратной связи
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Запускает сервер обратной связи"""
    print("🚀 Запуск сервера обратной связи...")
    
    # Проверяем, что файл существует
    feedback_server_path = Path("feedback_server.py")
    if not feedback_server_path.exists():
        print("❌ Файл feedback_server.py не найден!")
        sys.exit(1)
    
    try:
        # Запускаем сервер
        print("📡 Сервер обратной связи запущен на http://localhost:5001")
        print("📝 Эндпоинт: POST /feedback")
        print("🏥 Проверка здоровья: GET /health")
        print("⏹️  Для остановки нажмите Ctrl+C")
        print("-" * 50)
        
        subprocess.run([sys.executable, "feedback_server.py"])
        
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 