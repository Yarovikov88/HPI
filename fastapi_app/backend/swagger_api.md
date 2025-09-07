# HPI API — Документация

## Эндпоинты

### Auth

#### `POST /api/auth/register`
**Описание:** Регистрация пользователя  
**Параметры:**
- `email` (string, body)
- `password` (string, body)
- `full_name` (string, body)
**Ответы:**
- `200 OK` — Пользователь зарегистрирован

#### `POST /api/auth/login`
**Описание:** Вход пользователя  
**Параметры:**
- `email` (string, body)
- `password` (string, body)
**Ответы:**
- `200 OK` — Токен доступа

---

### Pro

#### `GET /api/pro/questions/{category}`
**Описание:** Получить PRO-вопросы по категории (problems, goals, blockers, metrics, achievements)  
**Параметры:**
- `category` (path, string)
- `lang` (query, string, опционально)
**Ответы:**
- `200 OK` — Список вопросов

#### `POST /api/pro/answers/{category}`
**Описание:** Отправить ответы по категории  
**Параметры:**
- `category` (path, string)
- `answers` (body, массив объектов ProAnswer)
**Ответы:**
- `200 OK` — Ответы сохранены

#### `GET /api/pro/answers/{category}`
**Описание:** Получить ответы по категории  
**Параметры:**
- `category` (path, string)
**Ответы:**
- `200 OK` — Список ответов

---

### Questions

#### `GET /api/questions`
**Описание:** Получить базовые вопросы  
**Параметры:**
- `lang` (query, string, опционально)
**Ответы:**
- `200 OK` — Список вопросов

#### `POST /api/answers`
**Описание:** Отправить базовые ответы  
**Параметры:**
- `answers` (body, массив объектов BasicAnswer)
**Ответы:**
- `200 OK` — Ответы сохранены

#### `GET /api/answers`
**Описание:** Получить базовые ответы  
**Параметры:** —
**Ответы:**
- `200 OK` — Список ответов

---

### Profile

#### `GET /api/profile`
**Описание:** Получить профиль пользователя  
**Параметры:** —
**Ответы:**
- `200 OK` — Данные профиля

#### `PUT /api/profile`
**Описание:** Обновить профиль пользователя  
**Параметры:**
- `full_name` (string, body, опционально)
- `language` (string, body, опционально)
**Ответы:**
- `200 OK` — Профиль обновлён

---

### Dashboard

#### `GET /api/dashboard`
**Описание:** Get Dashboard  
**Параметры:** —  
**Ответы:**
- `200 OK` — Успешный ответ  
  **Тип:** `application/json`  
  **Пример:**  
  ```
  "string"
  ```

---

### Trend

#### `GET /api/trend`
**Описание:** Get Trend  
**Параметры:** —  
**Ответы:**
- `200 OK` — Успешный ответ  
  **Тип:** `application/json`  
  **Пример:**  
  ```
  "string"
  ```

---

### Radar

#### `GET /api/radar`
**Описание:** Get Radar  
**Параметры:** —  
**Ответы:**
- `200 OK` — Успешный ответ  
  **Тип:** `application/json`  
  **Пример:**  
  ```
  "string"
  ```

---

### Recommendations

#### `GET /api/recommendations/basic`
**Описание:** Get Basic Recommendations  
**Параметры:**
- `lang` (query, string) — Язык  
**Ответы:**
- `200 OK` — Успешный ответ  
  **Тип:** `application/json`  
  **Пример:**  
  ```
  "string"
  ```
- `422 Validation Error`  
  **Тип:** `application/json`  
  **Пример:**  
  ```json
  {
    "detail": [
      {
        "loc": ["string", 0],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```

#### `GET /api/recommendations/ai`
**Описание:** Get Ai Recommendations  
**Параметры:** —  
**Ответы:**
- `200 OK` — Успешный ответ  
  **Тип:** `application/json`  
  **Пример:**  
  ```
  "string"
  ```

#### `GET /api/recommendations/history`
**Описание:** Get Recommendations History  
**Параметры:** —  
**Ответы:**
- `200 OK` — Успешный ответ  
  **Тип:** `application/json`  
  **Пример:**  
  ```
  "string"
  ```

---

### Default

#### `GET /`
**Описание:** Read Root  
**Параметры:** —  
**Ответы:**
- `200 OK` — Успешный ответ  
  **Тип:** `application/json`  
  **Пример:**  
  ```
  "string"
  ```

#### `GET /health`
**Описание:** Health Check  
**Параметры:** —  
**Ответы:**
- `200 OK` — Успешный ответ  
  **Тип:** `application/json`  
  **Пример:**  
  ```
  "string"
  ```

---

## Схемы (Schemas)

### BasicAnswer
Тип: object

### HTTPValidationError
Тип: object

### ProAnswer
Тип: object

### UserCreate
Тип: object

### UserLogin
Тип: object

### ValidationError
Тип: object  
**Пример:**  
```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
``` 