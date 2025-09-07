from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import SessionLocal
from app.models import Problem, Goal, Blocker, Metric, Achievement, User
from app.auth import get_current_user_id
from typing import List, Literal
from pydantic import BaseModel
import json
from datetime import datetime, date
from sqlalchemy import text as sa_text

router = APIRouter()

# Параметры подключения к БД (больше не используются, так как используем SQLAlchemy)
# DB_HOST = '83.147.192.188'
# DB_PORT = 5433
# DB_NAME = 'hpi_db'
# DB_USER = 'hpi_user'
# DB_PASSWORD = 'hpi_password_2024'

async def get_db():
    async with SessionLocal() as session:
        yield session

async def get_current_pro_user(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user or not user.is_pro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature is available for PRO users only."
        )
    return user

PRO_CATEGORIES = {
    "problems": Problem,
    "goals": Goal,
    "blockers": Blocker,
    "metrics": Metric,
    "achievements": Achievement,
}

class ProAnswer(BaseModel):
    sphere: int
    text: str
    date: date  # Исправлено: теперь это объект datetime.date

async def get_user_language(user_id: int, db: AsyncSession) -> str:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    return getattr(user, "language", "ru") if user else "ru"

def extract_question_from_fields(fields_json):
    """Извлекает реальный вопрос из JSON fields"""
    try:
        if not fields_json:
            return "Опишите подробно"
        
        fields = json.loads(fields_json) if isinstance(fields_json, str) else fields_json
        
        # Для metrics - особый случай с несколькими полями
        if 'goal' in fields and 'name' in fields:
            # Проверяем, есть ли дополнительные поля для метрик
            metric_fields = []
            if 'name' in fields:
                metric_fields.append(fields['name'].get('question', 'Название метрики'))
            if 'goal' in fields:
                metric_fields.append(fields['goal'].get('question', 'Желаемое значение'))
            if 'type' in fields:
                metric_fields.append(fields['type'].get('question', 'Тип метрики'))
            if 'unit' in fields:
                metric_fields.append(fields['unit'].get('question', 'Единица измерения'))
            if 'value' in fields:
                metric_fields.append(fields['value'].get('question', 'Текущее значение'))
            
            # Объединяем все поля метрики
            if len(metric_fields) >= 2:
                return f"{metric_fields[0]} и {metric_fields[1]}"
            elif len(metric_fields) == 1:
                return metric_fields[0]
            else:
                return "Опишите метрику"
        
        # Для остальных - ищем text.question
        if 'text' in fields and isinstance(fields['text'], dict):
            return fields['text'].get('question', 'Опишите подробно')
        
        # Если не нашли question, возвращаем первый text
        for field_name, field_data in fields.items():
            if isinstance(field_data, dict) and 'question' in field_data:
                return field_data['question']
        
        # Если fields содержит простую структуру без question, используем description или заглушку
        if 'text' in fields:
            return "Опишите подробно"
        
        return "Опишите подробно"
    except:
        return "Опишите подробно"

async def load_pro_questions_from_db(category, db: AsyncSession):
    """Загружает PRO вопросы напрямую из БД используя асинхронный SQLAlchemy"""
    try:
        # Используем асинхронный SQLAlchemy вместо psycopg2
        result = await db.execute(sa_text("""
            SELECT id, sphere, text, description, fields
            FROM questions 
            WHERE type = 'pro' AND category = :category
            ORDER BY sphere, id
        """), {"category": category})
        
        pro_questions = result.fetchall()
        
        # Группируем по сферам
        questions_by_sphere = {}
        sphere_mapping = {
            'love': '1', 'family': '2', 'friends': '3', 'career': '4',
            'physical': '5', 'mental': '6', 'hobby': '7', 'wealth': '8'
        }
        
        for row in pro_questions:
            question_id, sphere, text, description, fields = row
            sphere_key = sphere_mapping.get(sphere, sphere)
            
            if sphere_key not in questions_by_sphere:
                questions_by_sphere[sphere_key] = []
            
            # Для всех PRO категорий используем description, так как fields содержит только схему
            real_question = description if description else f"Опишите {category}"
            
            # Для метрик добавляем хардкод метрик, так как в БД их нет
            fields_data = fields if fields else {}
            if category == 'metrics':
                # Добавляем метрики для каждой сферы
                metrics_data = get_metrics_for_sphere(sphere_key)
                fields_data = {'metrics': metrics_data}
            
            questions_by_sphere[sphere_key].append({
                'id': question_id,
                'text': real_question,
                'description': description,
                'fields': fields_data,
                'original_text': text  # Сохраняем оригинальный текст для контекста
            })
        
        return questions_by_sphere
        
    except Exception as e:
        print(f"Error loading PRO questions from DB: {e}")
        return {}

def get_metrics_for_sphere(sphere_key):
    """Возвращает метрики для конкретной сферы"""
    metrics_map = {
        '1': [  # love
            {"name": "Число проводимых мероприятий в неделе с любимыми", "unit": "шт/нед", "type": "number"}
        ],
        '2': [  # family
            {"name": "Число проводимых мероприятий в неделе с родными", "unit": "шт/нед", "type": "number"}
        ],
        '3': [  # friends
            {"name": "Число проводимых мероприятий в неделе с друзьями", "unit": "шт/нед", "type": "number"}
        ],
        '4': [  # career
            {"name": "Деловых активностей в неделю (встречи, обучение, презентации, сделки, продажи)", "unit": "шт/нед", "type": "number"}
        ],
        '5': [  # physical
            {"name": "Активностей или тренировок в неделе", "unit": "шт/нед", "type": "number"}
        ],
        '6': [  # mental
            {"name": "Активностей для поддержания ментального здоровья в неделе (медитации, прогулки, чтение книг и др.)", "unit": "шт/нед", "type": "number"}
        ],
        '7': [  # hobby
            {"name": "Активностей связанных с хобби и увлечениями в неделе", "unit": "шт/нед", "type": "number"}
        ],
        '8': [  # wealth
            {"name": "Месячный доход", "unit": "₽/мес", "type": "number"}
        ]
    }
    return metrics_map.get(sphere_key, [])

@router.get("/questions/{category}")
async def get_pro_questions(
    category: Literal["problems", "goals", "blockers", "metrics", "achievements"],
    lang: str = None,
    # user: User = Depends(get_current_pro_user),  # Временно отключаем аутентификацию
    db: AsyncSession = Depends(get_db),
):
    """Получить PRO вопросы из базы данных"""
    try:
        if category not in PRO_CATEGORIES:
            raise HTTPException(status_code=404, detail="Unknown PRO category")
        
        # Загружаем вопросы напрямую из БД
        questions_by_sphere = await load_pro_questions_from_db(category, db)
        
        # Маппинг сфер для контекста
        sphere_names = {
            '1': 'отношениях с любимыми',
            '2': 'отношениях с родными', 
            '3': 'дружбе',
            '4': 'карьере',
            '5': 'физическом здоровье',
            '6': 'ментальном здоровье',
            '7': 'хобби и увлечениях',
            '8': 'благосостоянии'
        }
        
        # Преобразуем в формат API
        result = []
        for sphere_key in sorted(questions_by_sphere.keys()):
            sphere_questions = questions_by_sphere[sphere_key]
            
            if sphere_questions:  # Только если есть вопросы
                for q in sphere_questions:
                    # Для метрик не добавляем контекст сферы, так как текст уже содержит его
                    if category == 'metrics':
                        result.append({
                            "sphere": int(sphere_key),
                            "id": q['id'],
                            "text": q['text'],  # Используем оригинальный текст без добавления контекста
                            "description": q.get('description', ''),
                            "fields": q.get('fields', {}),
                            "original_text": q.get('original_text', ''),
                            "category": category
                        })
                    else:
                        # Для других категорий добавляем контекст как раньше
                        sphere_context = sphere_names.get(sphere_key, f'сфере {sphere_key}')
                        contextual_question = f"{q['text']} в {sphere_context}"
                        
                        result.append({
                            "sphere": int(sphere_key),
                            "id": q['id'],
                            "text": contextual_question,
                            "description": q.get('description', ''),
                            "fields": q.get('fields', {}),
                            "original_text": q.get('original_text', ''),
                            "category": category
                        })
        
        return result
    except Exception as e:
        print(f"Error loading PRO questions: {e}")
        # Fallback к заглушкам если что-то пошло не так
        return [
            {"sphere": i, "text": f"Опишите ваши {category} в сфере {i}", "category": category} 
            for i in range(1, 9)
        ]

@router.post("/answers/{category}")
async def post_pro_answers(
    category: Literal["problems", "goals", "blockers", "metrics", "achievements"],
    answers: List[ProAnswer],
    user: User = Depends(get_current_pro_user),
    db: AsyncSession = Depends(get_db),
):
    print(f"🚀 POST /answers/{category} вызван")
    print(f"📊 Получено {len(answers)} ответов")
    print(f"👤 Пользователь ID: {user.id}")
    
    # Детальная отладка каждого ответа
    for i, ans in enumerate(answers):
        print(f"📝 Ответ {i+1}:")
        print(f"   sphere: {ans.sphere} (тип: {type(ans.sphere)})")
        print(f"   text: {ans.text} (тип: {type(ans.text)})")
        print(f"   date: {ans.date} (тип: {type(ans.date)})")
        print(f"   date.isoformat(): {ans.date.isoformat() if hasattr(ans.date, 'isoformat') else 'НЕТ МЕТОДА'}")
    
    if category not in PRO_CATEGORIES:
        raise HTTPException(status_code=404, detail="Unknown PRO category")
    
    Model = PRO_CATEGORIES[category]
    saved_answers = []
    
    try:
        from sqlalchemy import func
        for ans in answers:
            # Ищем по user_id + sphere (+ name для metrics) + exact date (не created_at)
            filters = [
                Model.user_id == user.id,
                Model.sphere == ans.sphere,
                Model.date == ans.date  # Исправлено: ans.date уже объект date
            ]
            if category == "metrics":
                # Для metrics текст хранится в поле name
                filters.pop()  # убираем date=ans.date, заменим на явный cast при сравнении
                filters.append(Model.date == ans.date)  # Исправлено: ans.date уже объект date
            
            existing = await db.execute(select(Model).where(*filters))
            existing_answer = existing.scalar_one_or_none()
            
            if existing_answer:
                if category == "achievements":
                    existing_answer.description = ans.text
                elif category == "metrics":
                    existing_answer.name = ans.text
                else:
                    existing_answer.text = ans.text
                saved_answers.append(existing_answer)
            else:
                # Создаем запись с явной датой
                if category == "achievements":
                    new_answer = Model(
                        user_id=user.id,
                        sphere=ans.sphere,
                        description=ans.text,
                        date=ans.date
                    )
                elif category == "metrics":
                    new_answer = Model(
                        user_id=user.id,
                        sphere=ans.sphere,
                        name=ans.text,
                        date=ans.date
                    )
                else:
                    new_answer = Model(
                        user_id=user.id,
                        sphere=ans.sphere,
                        text=ans.text,
                        date=ans.date
                    )
                db.add(new_answer)
                saved_answers.append(new_answer)
        
        await db.commit()
        
        return [
            {
                "id": answer.id,
                "sphere": answer.sphere,
                "text": answer.description if category == "achievements" else (answer.name if category == "metrics" else answer.text),
                "date": answers[0].date.isoformat()  # Исправлено: преобразуем date в строку
            }
            for answer in saved_answers
        ]
    except Exception as e:
        print(f"Error saving {category} answers: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения ответов по категории '{category}'")

@router.get("/answers/{category}")
async def get_pro_answers(
    category: Literal["problems", "goals", "blockers", "metrics", "achievements"],
    date: str,  # Обязательный query параметр
    user: User = Depends(get_current_pro_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        if category not in PRO_CATEGORIES:
            raise HTTPException(status_code=404, detail="Unknown PRO category")

        # Валидация формата даты YYYY-MM-DD
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format, expected YYYY-MM-DD")
        
        # SQLite совместимые запросы по категориям
        if category in {"problems", "goals", "blockers"}:
            sql = f"""
                SELECT id, user_id, date, '{category}' AS category, sphere, text AS text, created_at
                FROM {category}
                WHERE user_id = :user_id AND date = :date
                ORDER BY id DESC
            """
        elif category == "metrics":
            sql = """
                SELECT id, user_id, date, 'metrics' AS category, sphere, name AS text, created_at
                FROM metrics
                WHERE user_id = :user_id AND date = :date
                ORDER BY id DESC
            """
        else:  # achievements
            sql = """
                SELECT id, user_id, date, 'achievements' AS category, sphere, description AS text, created_at
                FROM achievements
                WHERE user_id = :user_id AND date = :date
                ORDER BY id DESC
            """
        
        result = await db.execute(sa_text(sql), {"user_id": user.id, "date": date})
        rows = result.mappings().all()

        return [
            {
                "id": row["id"],
                "user_id": row["user_id"],
                "date": row["date"],
                "category": row["category"],
                "sphere": row["sphere"],
                "text": row["text"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting {category} answers: {e}")
        # Если есть ошибка, возвращаем пустой список
        return [] 

@router.get("/completion-status")
async def get_pro_completion_status(
    user_id: int = Depends(get_current_user_id),
    date: str = Query(..., description="Дата в формате YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить статус завершения PRO опроса по каждой сфере жизни
    """
    try:
        # Получаем все PRO ответы для пользователя на указанную дату
        categories = ["problems", "goals", "blockers", "metrics", "achievements"]
        
        # Собираем все ответы по категориям
        all_answers = {}
        for category in categories:
            if category in {"problems", "goals", "blockers"}:
                sql = f"""
                    SELECT id, user_id, date, '{category}' AS category, sphere, text AS text, created_at
                    FROM {category}
                    WHERE user_id = :user_id AND date = :date
                    ORDER BY id DESC
                """
            elif category == "metrics":
                sql = """
                    SELECT id, user_id, date, 'metrics' AS category, sphere, name AS text, created_at
                    FROM metrics
                    WHERE user_id = :user_id AND date = :date
                    ORDER BY id DESC
                """
            else:  # achievements
                sql = """
                    SELECT id, user_id, date, 'achievements' AS category, sphere, description AS text, created_at
                    FROM achievements
                    WHERE user_id = :user_id AND date = :date
                    ORDER BY id DESC
                """
            
            result = await db.execute(sa_text(sql), {"user_id": user_id, "date": date})
            answers = result.fetchall()
            
            for answer in answers:
                sphere_id = answer.sphere
                key = f"{category}-{sphere_id}"
                all_answers[key] = {
                    "id": answer.id,
                    "category": answer.category,
                    "sphere": answer.sphere,
                    "text": answer.text,
                    "date": answer.date,
                    "created_at": answer.created_at
                }
        
        # Определяем сферы жизни (1-8)
        spheres = list(range(1, 9))
        
        # Проверяем завершенность каждой сферы
        sphere_completion = {}
        for sphere_id in spheres:
            sphere_complete = True
            
            # Проверяем все категории для данной сферы
            for category in categories:
                key = f"{category}-{sphere_id}"
                answer = all_answers.get(key)
                
                # Если нет ответа или ответ пустой, сфера не завершена
                if not answer or not answer.get("text") or not answer["text"].strip():
                    sphere_complete = False
                    break
            
            sphere_completion[f"sphere_{sphere_id}"] = {
                "sphere_id": sphere_id,
                "is_complete": sphere_complete,
                "categories": {
                    category: {
                        "has_answer": bool(all_answers.get(f"{category}-{sphere_id}")),
                        "answer_text": all_answers.get(f"{category}-{sphere_id}", {}).get("text", "")
                    }
                    for category in categories
                }
            }
        
        # Общий статус PRO опроса
        overall_complete = all(sphere["is_complete"] for sphere in sphere_completion.values())
        
        return {
            "date": date,
            "user_id": user_id,
            "overall_complete": overall_complete,
            "spheres": sphere_completion,
            "total_spheres": len(spheres),
            "completed_spheres": sum(1 for sphere in sphere_completion.values() if sphere["is_complete"])
        }
        
    except Exception as e:
        print(f"Ошибка при получении статуса завершения PRO опроса: {e}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}") 