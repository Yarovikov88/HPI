import asyncio
from app.db import engine
from app.models import Base

async def create_tables():
    print("🚀 Создание таблиц в базе данных...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы созданы успешно!")
    except Exception as e:
        print(f"❌ Ошибка создания таблиц: {e}")
        import traceback
        print(f"📋 Полный traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(create_tables()) 