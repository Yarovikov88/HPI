import asyncio
import asyncpg
from sqlalchemy import text
from app.db import engine

async def inspect_database():
    """Инспектирует базу данных и выводит все таблицы и их структуру"""
    
    print("🔍 ИНСПЕКЦИЯ БАЗЫ ДАННЫХ")
    print("=" * 50)
    
    try:
        # Подключаемся к БД
        async with engine.begin() as conn:
            print("✅ Подключение к БД успешно")
            
            # Получаем список всех таблиц
            print("\n📋 СПИСОК ВСЕХ ТАБЛИЦ:")
            print("-" * 30)
            
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            
            if not tables:
                print("❌ Таблиц не найдено")
                return
            
            for i, (table_name,) in enumerate(tables, 1):
                print(f"{i}. {table_name}")
            
            # Получаем структуру каждой таблицы
            print(f"\n🏗️ СТРУКТУРА ТАБЛИЦ ({len(tables)} таблиц):")
            print("=" * 50)
            
            for table_name, in tables:
                print(f"\n📊 ТАБЛИЦА: {table_name}")
                print("-" * 30)
                
                # Получаем информацию о колонках
                result = await conn.execute(text("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default,
                        character_maximum_length
                    FROM information_schema.columns 
                    WHERE table_name = :table_name 
                    ORDER BY ordinal_position
                """), {"table_name": table_name})
                
                columns = result.fetchall()
                
                print(f"{'Колонка':<20} {'Тип':<15} {'NULL':<5} {'По умолчанию':<15} {'Макс. длина':<10}")
                print("-" * 70)
                
                for col_name, data_type, is_nullable, col_default, max_length in columns:
                    nullable = "YES" if is_nullable == "YES" else "NO"
                    default = str(col_default) if col_default else ""
                    max_len = str(max_length) if max_length else ""
                    
                    print(f"{col_name:<20} {data_type:<15} {nullable:<5} {default:<15} {max_len:<10}")
                
                # Получаем количество записей
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                print(f"\n📈 Записей в таблице: {count}")
                
                # Показываем примеры данных (первые 3 записи)
                if count > 0:
                    print("\n📝 ПРИМЕРЫ ДАННЫХ:")
                    result = await conn.execute(text(f"SELECT * FROM {table_name} LIMIT 3"))
                    sample_data = result.fetchall()
                    
                    for i, row in enumerate(sample_data, 1):
                        print(f"  Запись {i}: {row}")
                
                print("\n" + "=" * 50)
            
            # Получаем информацию о внешних ключах
            print(f"\n🔗 ВНЕШНИЕ КЛЮЧИ:")
            print("-" * 30)
            
            result = await conn.execute(text("""
                SELECT 
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                ORDER BY tc.table_name, kcu.column_name
            """))
            
            foreign_keys = result.fetchall()
            
            if foreign_keys:
                for table_name, column_name, foreign_table, foreign_column in foreign_keys:
                    print(f"  {table_name}.{column_name} → {foreign_table}.{foreign_column}")
            else:
                print("  Внешних ключей не найдено")
            
            print(f"\n✅ Инспекция завершена. Найдено таблиц: {len(tables)}")
            
    except Exception as e:
        print(f"❌ Ошибка при инспекции БД: {e}")
        print(f"Детали: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(inspect_database()) 