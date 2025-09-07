import os

def check_openai_available():
    """
    Проверяет доступность OpenAI API и корректность ключа.
    Возвращает None, если всё ок, либо строку с ошибкой.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OPENAI_API_KEY не найден в переменных окружения"
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        # Простой echo-запрос
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1,
            timeout=10
        )
        return None  # Всё ок
    except Exception as e:
        return str(e) 