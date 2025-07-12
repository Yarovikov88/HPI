import requests
import json
from datetime import datetime

# --- Конфигурация ---
BASE_URL = "http://localhost:8000"
ENDPOINT = "/api/v1/pro-answers/"
FULL_URL = f"{BASE_URL}{ENDPOINT}"

# --- Моковые данные ---
# Создаем полезную нагрузку в соответствии со схемой ProAnswersPayload
payload = {
    "achievements": [
        {
            "sphere_id": "love",
            "description": "Провел замечательный вечер с семьей",
            "date_achieved": datetime.now().isoformat()
        }
    ],
    "problems": [
        {
            "sphere_id": "work",
            "text": "Слишком много отвлекающих факторов",
            "severity": 3
        }
    ],
    "goals": [
        {
            "sphere_id": "health",
            "text": "Начать бегать по утрам",
            "deadline": "2025-08-01T00:00:00",
            "priority": 1
        }
    ],
    "blockers": [
        {
            "sphere_id": "love",
            "text": "Недостаток времени из-за работы",
            "impact_level": 4
        }
    ],
    "metrics": [
        {
            "sphere_id": "money",
            "name": "Сбережения",
            "current_value": 50000,
            "target_value": 100000,
            "unit": "руб."
        }
    ]
}

# --- Отправка запроса ---
try:
    print(f"Отправка POST-запроса на: {FULL_URL}")
    print("Тело запроса:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    response = requests.post(FULL_URL, json=payload, headers={"Content-Type": "application/json"})

    # --- Вывод результата ---
    print(f"\nСтатус-код ответа: {response.status_code}")

    try:
        response_json = response.json()
        print("Ответ сервера (JSON):")
        print(json.dumps(response_json, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print("Ответ сервера (не JSON):")
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f"\nПроизошла ошибка при отправке запроса: {e}") 