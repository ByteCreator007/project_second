import asyncio
from src.database import async_session
from src.models import PackageType
from sqlalchemy import text

async def seed_package_types():
    async with async_session() as session:
        # Проверяем, есть ли уже записи в таблице
        result = await session.execute(text("SELECT COUNT(*) FROM package_types"))
        count = result.scalar()
        if count == 0:
            package_types = [
                PackageType(name="одежда"),
                PackageType(name="электроника"),
                PackageType(name="разное")
            ]
            session.add_all(package_types)
            await session.commit()
            print("Начальные типы посылок добавлены.")
        else:
            print("Типы посылок уже существуют.")

if __name__ == "__main__":
    asyncio.run(seed_package_types())
