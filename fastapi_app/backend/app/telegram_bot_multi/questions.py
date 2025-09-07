# src/telegram_bot_multi/questions.py

import json
from typing import List, Dict, Any
from .db import get_connection

class QuestionsManager:
    def __init__(self, lang='ru'):
        self.lang = lang
        self.questions_data = self._load_questions()
        
    def _load_questions(self) -> Dict[str, Any]:
        """Загружает вопросы из базы данных"""
        questions_data = {}
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # Загружаем базовые вопросы
            cur.execute("""
                SELECT id, sphere, text, options, scores 
                FROM questions 
                WHERE type = 'basic'
                ORDER BY sphere, id
            """)
            
            basic_questions = cur.fetchall()
            
            for row in basic_questions:
                question_id, sphere, text, options, scores = row
                
                # Преобразуем sphere в номер (love->1, family->2, etc.)
                sphere_mapping = {
                    'love': '1', 'family': '2', 'friends': '3', 'career': '4',
                    'physical': '5', 'mental': '6', 'hobby': '7', 'wealth': '8'
                }
                sphere_key = sphere_mapping.get(sphere, sphere)
                
                if sphere_key not in questions_data:
                    questions_data[sphere_key] = {'basic': [], 'pro': []}
                
                question = {
                    'id': question_id,
                    'type': 'basic',
                    'text': text,
                    'options': options if options else [],
                    'scores': scores if scores else None
                }
                
                questions_data[sphere_key]['basic'].append(question)
            
            # Загружаем PRO вопросы
            cur.execute("""
                SELECT id, sphere, category, text, description, fields
                FROM questions 
                WHERE type = 'pro'
                ORDER BY sphere, id
            """)
            
            pro_questions = cur.fetchall()
            
            for row in pro_questions:
                question_id, sphere, category, text, description, fields = row
                
                # Преобразуем sphere в номер
                sphere_mapping = {
                    'love': '1', 'family': '2', 'friends': '3', 'career': '4',
                    'physical': '5', 'mental': '6', 'hobby': '7', 'wealth': '8'
                }
                sphere_key = sphere_mapping.get(sphere, sphere)
                
                if sphere_key not in questions_data:
                    questions_data[sphere_key] = {'basic': [], 'pro': []}
                
                question = {
                    'id': question_id,
                    'type': 'pro',
                    'category': category,
                    'text': text,
                    'description': description,
                    'fields': fields if fields else {}
                }
                
                questions_data[sphere_key]['pro'].append(question)
            
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"Error loading questions from database: {e}")
            return {}
                
        return questions_data

    def get_sphere(self, sphere_num: int):
        """Возвращает данные сферы"""
        sphere_key = str(sphere_num)
        if sphere_key not in self.questions_data:
            return None
            
        # Создаем объект сферы
        sphere_names = {
            '1': 'Отношения с любимыми' if self.lang == 'ru' else 'Relationships with loved ones',
            '2': 'Отношения с родными' if self.lang == 'ru' else 'Family relationships', 
            '3': 'Друзья' if self.lang == 'ru' else 'Friends',
            '4': 'Карьера' if self.lang == 'ru' else 'Career',
            '5': 'Физическое здоровье' if self.lang == 'ru' else 'Physical health',
            '6': 'Ментальное здоровье' if self.lang == 'ru' else 'Mental health',
            '7': 'Хобби и увлечения' if self.lang == 'ru' else 'Hobbies and interests',
            '8': 'Благосостояние' if self.lang == 'ru' else 'Well-being'
        }
        
        sphere_emojis = {
            '1': '💖', '2': '🏡', '3': '🤝', '4': '💼',
            '5': '🏋️', '6': '🧠', '7': '🎨', '8': '💰'
        }
        
        class Sphere:
            def __init__(self, num, name, emoji, questions):
                self.num = num
                self.name = name
                self.emoji = emoji
                self.questions = questions
                
        return Sphere(
            sphere_num,
            sphere_names.get(sphere_key, f'Sphere {sphere_num}'),
            sphere_emojis.get(sphere_key, ''),
            self.questions_data[sphere_key]['basic']
        )

    def format_question_for_telegram(self, sphere, question):
        """Форматирует вопрос для Telegram"""
        def esc(s):
            return str(s).replace('<', '&lt;').replace('>', '&gt;')
            
        text = f"{sphere.emoji} <b>{esc(sphere.name)}</b>\n\n"
        text += f"<b>{'Вопрос' if self.lang == 'ru' else 'Question'} {esc(str(question.get('id', '')))}:</b>\n{esc(question.get('text', ''))}\n\n"
        
        options = question.get('options', [])
        if options:
            text += f"<b>{'Варианты ответов' if self.lang == 'ru' else 'Answer options'}:</b>\n"
            for i, option in enumerate(options, 1):
                text += f"{i}. {esc(option)}\n"
                
        return text

    def get_pro_questions(self, sphere_num: int) -> List[Dict[str, Any]]:
        """Возвращает PRO вопросы для сферы"""
        sphere_key = str(sphere_num)
        if sphere_key not in self.questions_data:
            return []
        return self.questions_data[sphere_key].get('pro', [])
        
    def get_pro_questions_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Возвращает PRO вопросы по категории"""
        all_pro_questions = []
        for sphere_data in self.questions_data.values():
            for question in sphere_data.get('pro', []):
                if question.get('category') == category:
                    all_pro_questions.append(question)
        return all_pro_questions 