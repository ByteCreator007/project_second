import asyncio
from src.database import engine
from src.models import Base

async def init_db():
    async with engine.begin() as conn:
        # Создаем все таблицы, если они ещё не созданы
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
    print("Tables created successfully.")

