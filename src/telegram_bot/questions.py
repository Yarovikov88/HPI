"""
Модуль для работы с вопросами в Telegram-боте HPI
"""
import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Question:
    """Структура вопроса."""
    id: str
    text: str
    options: List[str]
    scores: List[int]
    inverse: bool = False


@dataclass
class Sphere:
    """Структура сферы жизни."""
    number: int
    name: str
    emoji: str
    questions: List[Question]


class QuestionsManager:
    """Менеджер вопросов для бота."""
    
    def __init__(self, database_path: Optional[str] = None):
        if database_path is None:
            # Определяем путь к базе данных
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            database_path = os.path.join(project_root, 'database', 'questions.md')
        
        self.database_path = database_path
        self.spheres = self._load_spheres()
    
    def _load_spheres(self) -> List[Sphere]:
        """Загружает сферы из базы данных."""
        spheres_config = [
            {"number": 1, "name": "Отношения с любимыми", "emoji": "💖"},
            {"number": 2, "name": "Отношения с родными", "emoji": "🏡"},
            {"number": 3, "name": "Друзья", "emoji": "🤝"},
            {"number": 4, "name": "Карьера", "emoji": "💼"},
            {"number": 5, "name": "Физическое здоровье", "emoji": "♂️"},
            {"number": 6, "name": "Ментальное здоровье", "emoji": "🧠"},
            {"number": 7, "name": "Хобби и увлечения", "emoji": "🎨"},
            {"number": 8, "name": "Благосостояние", "emoji": "💰"}
        ]
        
        spheres = []
        
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for config in spheres_config:
                sphere_questions = self._parse_sphere_questions(content, config)
                sphere = Sphere(
                    number=config["number"],
                    name=config["name"],
                    emoji=config["emoji"],
                    questions=sphere_questions
                )
                spheres.append(sphere)
                
        except Exception as e:
            print(f"Ошибка загрузки вопросов: {e}")
            # Возвращаем базовые вопросы если файл недоступен
            spheres = self._get_fallback_spheres()
        
        return spheres
    
    def _parse_sphere_questions(self, content: str, sphere_config: Dict) -> List[Question]:
        """Парсит вопросы для конкретной сферы."""
        import re
        
        questions = []
        emoji = sphere_config["emoji"]
        name = sphere_config["name"]
        
        # Ищем JSON-блок для сферы
        pattern = rf"##\s*{re.escape(emoji)}\s*{re.escape(name)}\n```json\n([\s\S]+?)\n```"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            try:
                json_data = json.loads(match.group(1))
                for item in json_data:
                    if item.get("type") == "basic" and "id" in item:
                        question = Question(
                            id=item["id"],
                            text=item["text"],
                            options=item["options"],
                            scores=item.get("scores", [1, 2, 3, 4]),
                            inverse=item.get("inverse", False)
                        )
                        questions.append(question)
            except json.JSONDecodeError:
                pass
        
        # Берем только первые 6 вопросов
        return questions[:6]
    
    def _get_fallback_spheres(self) -> List[Sphere]:
        """Возвращает базовые вопросы если файл недоступен."""
        fallback_questions = [
            Question(
                id="1.1",
                text="Как часто вы проводите качественное время вместе?",
                options=["Редко или никогда", "Иногда", "Часто", "Регулярно и осознанно"],
                scores=[1, 2, 3, 4]
            ),
            Question(
                id="1.2", 
                text="Синхронизация жизненных целей",
                options=["У нас совершенно разные планы", "Есть частичное совпадение", "В основном совпадают", "Полностью синхронизированы"],
                scores=[1, 2, 3, 4]
            ),
            Question(
                id="1.3",
                text="Решение конфликтов", 
                options=["Частые ссоры без решения", "Иногда споры, но компромиссы", "Редкие конфликты, конструктив", "Практически никогда не конфликтуем"],
                scores=[4, 3, 2, 1],
                inverse=True
            ),
            Question(
                id="1.4",
                text="Поддержка в кризисах",
                options=["Партнёр не участвует", "Минимальная помощь", "Активно поддерживает", "Полная совместная работа"],
                scores=[1, 2, 3, 4]
            ),
            Question(
                id="1.5",
                text="Проявление внимания и заботы",
                options=["Редко или никогда", "Иногда", "Часто", "Постоянно и разнообразно"],
                scores=[1, 2, 3, 4]
            ),
            Question(
                id="1.6",
                text="Ощущение любви и принятия",
                options=["Совсем нет / В слабой степени", "В некоторой степени", "В значительной степени", "Абсолютно / Полностью"],
                scores=[1, 2, 3, 4]
            )
        ]
        
        spheres_config = [
            {"number": 1, "name": "Отношения с любимыми", "emoji": "💖"},
            {"number": 2, "name": "Отношения с родными", "emoji": "🏡"},
            {"number": 3, "name": "Друзья", "emoji": "🤝"},
            {"number": 4, "name": "Карьера", "emoji": "💼"},
            {"number": 5, "name": "Физическое здоровье", "emoji": "♂️"},
            {"number": 6, "name": "Ментальное здоровье", "emoji": "🧠"},
            {"number": 7, "name": "Хобби и увлечения", "emoji": "🎨"},
            {"number": 8, "name": "Благосостояние", "emoji": "💰"}
        ]
        
        spheres = []
        for config in spheres_config:
            sphere = Sphere(
                number=config["number"],
                name=config["name"],
                emoji=config["emoji"],
                questions=fallback_questions.copy()  # Копируем для каждой сферы
            )
            spheres.append(sphere)
        
        return spheres
    
    def get_sphere(self, sphere_number: int) -> Optional[Sphere]:
        """Получает сферу по номеру."""
        for sphere in self.spheres:
            if sphere.number == sphere_number:
                return sphere
        return None
    
    def get_question(self, sphere_number: int, question_index: int) -> Optional[Question]:
        """Получает вопрос по номеру сферы и индексу вопроса."""
        sphere = self.get_sphere(sphere_number)
        if sphere and 0 <= question_index < len(sphere.questions):
            return sphere.questions[question_index]
        return None
    
    def get_total_questions(self) -> int:
        """Возвращает общее количество вопросов."""
        return sum(len(sphere.questions) for sphere in self.spheres)
    
    def format_question_for_telegram(self, sphere: Sphere, question: Question) -> str:
        """Форматирует вопрос для отображения в Telegram."""
        text = f"{sphere.emoji} <b>{sphere.name}</b>\n\n"
        text += f"<b>Вопрос {question.id}:</b>\n{question.text}\n\n"
        text += "<b>Варианты ответов:</b>\n"
        
        for i, option in enumerate(question.options, 1):
            text += f"{i}. {option}\n"
        
        return text 