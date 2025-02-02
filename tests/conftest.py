import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from src.database import engine
from src.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    # Завершаем асинхронные генераторы
    loop.run_until_complete(loop.shutdown_asyncgens())
    # Отменяем все оставшиеся задачи, чтобы они не выполнялись после закрытия
    pending = asyncio.all_tasks(loop)
    for task in pending:
        task.cancel()
    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    # Явно закрываем engine, чтобы все соединения корректно завершились
    loop.run_until_complete(engine.dispose())
    loop.close()

# Асинхронная фикстура, возвращающая AsyncClient
@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
