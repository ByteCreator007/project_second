import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src import models, database
from src.utils import get_exchange_rate, set_exchange_rate

async def fetch_exchange_rate() -> float:
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
        rate = data.get("Valute", {}).get("USD", {}).get("Value")
        if not rate:
            raise Exception("Не удалось получить курс доллара")
        return float(rate)

async def calculate_shipping_costs():
    # Получаем курс доллара из кэша или извне
    rate = await get_exchange_rate()
    if not rate:
        rate = await fetch_exchange_rate()
        await set_exchange_rate(rate, ttl=300)

    async with database.async_session() as db:
        result = await db.execute(select(models.Package).where(models.Package.shipping_cost.is_(None)))
        packages = result.scalars().all()
        for pkg in packages:
            cost = (pkg.weight * 0.5 + pkg.content_value * 0.01) * rate
            pkg.shipping_cost = cost
        await db.commit()

# Функция для ручного запуска задачи (например, через специальный эндпоинт)
async def run_shipping_cost_task():
    try:
        await calculate_shipping_costs()
    except Exception as e:
        print(f"Ошибка при расчёте стоимости доставки: {e}")
