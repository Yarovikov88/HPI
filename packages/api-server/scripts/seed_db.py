import json
import os
import re
import sys
from sqlalchemy.orm import Session

# --- Настройка путей для импорта ---
# Добавляем корень 'api-server' в пути, чтобы импорты из 'src' работали
current_dir = os.path.dirname(os.path.abspath(__file__))
api_server_dir = os.path.dirname(current_dir) # Это 'scripts' -> 'api-server'
if api_server_dir not in sys.path:
    sys.path.insert(0, api_server_dir)

import database
import models
from database import Base

# --- Основная логика ---

def seed_database():
    """
    Заполняет базу данных вопросами и сферами из markdown-файла.
    """
    # Пересоздаем таблицы для чистоты данных
    Base.metadata.drop_all(bind=database.engine)
    Base.metadata.create_all(bind=database.engine)

    db: Session = database.SessionLocal()

    try:
        # Указываем путь к файлу
        project_root = os.path.dirname(api_server_dir) # 'api-server' -> 'packages'
        questions_file_path = os.path.join(project_root, '..', 'database', 'questions.md')
        
        with open(questions_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Регулярное выражение для поиска сфер и их JSON-блоков
        pattern = re.compile(r'##\s+(?P<emoji>[\U0001F300-\U0001F64F\U0001F680-\U0001F6FF\U00002600-\U000026FF\U00002700-\U000027BF]+)\s+(?P<name>.+?)\n+```json\n(?P<json_data>[\s\S]+?)\n```', re.DOTALL)
        
        # Сначала найдем таблицу со сферами для получения их ID
        spheres_map = {}
        table_pattern = re.compile(r'## Сферы \(spheres master list\)\n\n\|.+?\|\n\|(?P<table_data>[\s\S]+?)\n\n<!--', re.DOTALL)
        table_match = table_pattern.search(content)
        if table_match:
            table_data = table_match.group('table_data')
            rows = [row.strip() for row in table_data.strip().split('\n')]
            for row in rows:
                if not row.startswith('|'): continue
                cols = [col.strip() for col in row.split('|')][1:-1] # Убираем пустые строки от крайних |
                if len(cols) == 3:
                    short_name, full_name, emoji = cols
                    spheres_map[emoji] = {'id': short_name, 'name': full_name}


        for match in pattern.finditer(content):
            emoji = match.group('emoji').strip()
            sphere_name = match.group('name').strip()
            json_data = match.group('json_data').strip()
            
            sphere_info = spheres_map.get(emoji)
            if not sphere_info:
                print(f"Предупреждение: Не найден ID для сферы с эмодзи {emoji}")
                continue

            # Добавляем/обновляем сферу в БД
            sphere = db.query(models.Sphere).filter(models.Sphere.id == sphere_info['id']).first()
            if not sphere:
                sphere = models.Sphere(id=sphere_info['id'], name=sphere_name)
                db.add(sphere)
                db.commit()
            
            questions = json.loads(json_data)
            for q_data in questions:
                # Пропускаем вопросы без ID, так как они не являются реальными метриками
                if not q_data.get('id'):
                    continue

                question = models.Question(
                    id=q_data.get('id'),
                    sphere_id=sphere.id,
                    type=q_data.get('type'),
                    category=q_data.get('category'),
                    text=q_data.get('text'),
                    description=q_data.get('description'),
                    # Преобразуем сложные поля в JSON-строки для хранения
                    options=json.dumps(q_data.get('options')) if q_data.get('options') else None,
                    scores=json.dumps(q_data.get('scores')) if q_data.get('scores') else None,
                    fields=json.dumps(q_data.get('fields')) if q_data.get('fields') else None,
                    metrics=json.dumps(q_data.get('metrics')) if q_data.get('metrics') else None,
                    inverse=q_data.get('inverse', False)
                )
                db.add(question)

        db.commit()
        print("✅ База данных успешно заполнена.")

    except Exception as e:
        db.rollback()
        print(f"❌ Произошла ошибка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database() 