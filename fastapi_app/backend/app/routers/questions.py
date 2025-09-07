from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text as sa_text
from app.db import SessionLocal
from app.models import Answer, User, Question
from app.auth import get_current_user_id
from typing import List
from pydantic import BaseModel
from datetime import date as date_type
import json

router = APIRouter()

# Параметры подключения к БД (больше не используются, так как используем SQLAlchemy)
# DB_HOST = '83.147.192.188'
# DB_PORT = 5433
# DB_NAME = 'hpi_db'
# DB_USER = 'hpi_user'
# DB_PASSWORD = 'hpi_password_2024'

class BasicAnswer(BaseModel):
    sphere: int  # Сфера как число (1-8)
    question_id: str  # ID вопроса как строка
    answer: str  # Ответ как строка (согласно модели БД)
    date: str  # Дата для фильтрации

async def get_db():
    async with SessionLocal() as session:
        yield session

async def get_user_language(user_id: int, db: AsyncSession) -> str:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    return getattr(user, "language", "ru") if user else "ru"

async def load_questions_from_db(lang: str = 'ru', db: AsyncSession = None):
    """Загружает вопросы из БД используя модель Question"""
    try:
        print("🔌 Подключаемся к БД для загрузки вопросов...")
        
        if db is None:
            # Если db не передан, создаем новую сессию
            async with SessionLocal() as session:
                return await load_questions_from_db(lang, session)
        
        print(f"📋 Загружаем базовые вопросы для языка: {lang}")
        
        # Загружаем базовые вопросы с учетом языка используя SQLAlchemy ORM
        result = await db.execute(
            select(Question).where(
                Question.type == 'basic',
                Question.language == lang
            ).order_by(Question.sphere, Question.question_id)
        )
        
        basic_questions = result.scalars().all()
        print(f"✅ Загружено {len(basic_questions)} базовых вопросов")
        
        # Отладочная информация
        for q in basic_questions[:3]:  # Показываем первые 3 вопроса
            print(f"  - Вопрос: {q.question_id}, сфера: {q.sphere}, текст: {q.text[:50]}...")
        
        # Группируем по сферам
        questions_by_sphere = {}
        sphere_mapping = {
            'love': '1', 'family': '2', 'friends': '3', 'career': '4',
            'physical': '5', 'mental': '6', 'hobby': '7', 'wealth': '8'
        }
        
        for question in basic_questions:
            sphere_key = sphere_mapping.get(question.sphere, question.sphere)
            
            if sphere_key not in questions_by_sphere:
                questions_by_sphere[sphere_key] = []
            
            # Парсим JSON поля - проверяем тип данных
            if question.options and isinstance(question.options, str):
                options = json.loads(question.options)
            else:
                options = question.options if question.options else []
                
            if question.scores and isinstance(question.scores, str):
                scores = json.loads(question.scores)
            else:
                scores = question.scores if question.scores else None
            
            questions_by_sphere[sphere_key].append({
                'id': question.question_id,
                'text': question.text,
                'options': options,
                'scores': scores,
                'inverse': question.inverse
            })
        
        print(f"✅ Сгруппировано по {len(questions_by_sphere)} сферам")
        for sphere_key, questions in questions_by_sphere.items():
            print(f"  - Сфера {sphere_key}: {len(questions)} вопросов")
        
        return questions_by_sphere
        
    except Exception as e:
        print(f"❌ Ошибка загрузки вопросов из БД: {e}")
        return {}

@router.get("/questions")
async def get_basic_questions(
    lang: str = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Получить базовые вопросы из базы данных"""
    try:
        print("🚀 Запрос на получение базовых вопросов...")
        
        # Определяем язык
        if not lang:
            lang = await get_user_language(user_id, db)
        
        print(f"🌐 Используем язык: {lang}")
        
        # Загружаем вопросы из БД с учетом языка
        questions_by_sphere = await load_questions_from_db(lang, db)
        
        print(f"📊 Загружено данных для {len(questions_by_sphere)} сфер")
        print(f"🔍 Содержимое questions_by_sphere: {questions_by_sphere}")
        
        # Преобразуем в формат API
        result = []
        for sphere_key in sorted(questions_by_sphere.keys()):
            sphere_questions = questions_by_sphere[sphere_key]
            if sphere_questions:  # Только если есть вопросы
                # Проверяем, что sphere_key можно преобразовать в число
                try:
                    sphere_number = int(sphere_key)
                    result.append({
                        "sphere": sphere_number,
                        "questions": sphere_questions
                    })
                    print(f"✅ Добавлена сфера {sphere_key} с {len(sphere_questions)} вопросами")
                except ValueError:
                    print(f"⚠️ Пропускаем сферу {sphere_key} - не является числом")
                    continue
        
        print(f"🎯 Возвращаем {len(result)} сфер с вопросами")
        return result
    except Exception as e:
        print(f"❌ Ошибка в get_basic_questions: {e}")
        # Fallback к заглушкам если что-то пошло не так
        return [
            {"sphere": i, "questions": [
                {"id": f"{i}.{j}", "text": f"Вопрос {j} по сфере {i}", "options": ["1", "2", "3", "4"]} 
                for j in range(1, 7)
            ]} for i in range(1, 9)
        ]

@router.post("/answers")
async def post_basic_answers(
    answers: List[BasicAnswer],
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        print(f"🚀 Сохранение {len(answers)} ответов для пользователя {user_id}")
        saved_answers = []
        
        for ans in answers:
            print(f"📝 Обрабатываем ответ: сфера={ans.sphere}, вопрос={ans.question_id}, ответ={ans.answer}, дата={ans.date}")
            
            # Проверяем, существует ли уже ответ для этой даты (исправлено для SQLite)
            date_obj = date_type.fromisoformat(ans.date)
            existing = await db.execute(
                select(Answer).where(
                    Answer.user_id == user_id,
                    Answer.sphere == int(ans.sphere),
                    Answer.question_id == ans.question_id,
                    Answer.date == date_obj
                )
            )
            existing_answer = existing.scalar_one_or_none()
            
            if existing_answer:
                # Обновляем существующий ответ
                print(f"🔄 Обновляем существующий ответ ID: {existing_answer.id}")
                existing_answer.answer = str(ans.answer)  # Преобразуем в строку
                saved_answers.append(existing_answer)
            else:
                # Создаем новый ответ с явной датой (исправлено для SQLite)
                print(f"➕ Создаем новый ответ")
                # Преобразуем строку даты в объект date
                date_obj = date_type.fromisoformat(ans.date)
                new_answer = Answer(
                    user_id=user_id,
                    sphere=int(ans.sphere),  # Преобразуем в int
                    question_id=ans.question_id,
                    answer=str(ans.answer),  # Преобразуем в строку
                    date=date_obj
                )
                db.add(new_answer)
                saved_answers.append(new_answer)
        
        # Проверяем, не пора ли выдать PRO
        user = await db.get(User, user_id)
        if user and not user.is_pro:
            from sqlalchemy import func
            count_result = await db.execute(
                select(func.count(Answer.id)).where(Answer.user_id == user_id)
            )
            total_answers = count_result.scalar_one()
            
            if total_answers >= 10:
                user.is_pro = True
                db.add(user)

        print(f"💾 Выполняем commit в БД...")
        await db.commit()
        print(f"✅ Commit выполнен успешно!")
        
        # Возвращаем полные объекты с id
        result = [
            {
                "id": answer.id,
                "sphere": answer.sphere,
                "question_id": answer.question_id,
                "answer": answer.answer,
                "date": answers[0].date  # Используем дату из запроса
            }
            for answer in saved_answers
        ]
        print(f"📤 Возвращаем {len(result)} сохраненных ответов")
        return result
    except Exception as e:
        print(f"❌ Ошибка сохранения ответов: {e}")
        print(f"🔍 Тип ошибки: {type(e).__name__}")
        import traceback
        print(f"📋 Полный traceback: {traceback.format_exc()}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения ответов: {str(e)}")

@router.get("/answers")
async def get_basic_answers(
    date: str,  # Обязательный query параметр
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        print(f"🔍 Получение ответов для пользователя {user_id} на дату {date}")
        date_obj = date_type.fromisoformat(date)
        result = await db.execute(
            select(Answer).where(
                Answer.user_id == user_id,
                Answer.date == date_obj
            )
        )
        items = result.scalars().all()
        print(f"📊 Найдено {len(items)} ответов в БД")
        
        result_list = [
            {
                "id": item.id,
                "sphere": item.sphere,
                "question_id": item.question_id,
                "answer": item.answer,
                "date": date  # Возвращаем запрошенную дату
            }
            for item in items
        ]
        print(f"📤 Возвращаем {len(result_list)} ответов")
        return result_list
    except Exception as e:
        # Если есть ошибка, возвращаем пустой список
        print(f"❌ Ошибка получения ответов: {e}")
        import traceback
        print(f"📋 Полный traceback: {traceback.format_exc()}")
        return [] 