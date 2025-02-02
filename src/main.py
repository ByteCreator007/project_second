import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.routes import packages, package_types
from src import tasks, utils
from apscheduler.schedulers.asyncio import AsyncIOScheduler

app = FastAPI(title="Микросервис Службы международной доставки")

templates = Jinja2Templates(directory="templates")

# Подключаем роутеры для работы с посылками и типами посылок
app.include_router(packages.router)
app.include_router(package_types.router)

# Маршрут для веб-интерфейса
@app.get("/web", response_class=HTMLResponse)
async def get_web(request: Request):
    """
    Отображает веб-интерфейс для регистрации посылки.
    Шаблон index.html должен находиться в папке templates.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.on_event("startup")
async def startup_event():
    # Инициализируем Redis
    await utils.init_redis()
    # Запускаем планировщик для периодических задач (каждые 5 минут)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(tasks.run_shipping_cost_task, 'interval', minutes=5)
    scheduler.start()

if __name__ == "__main__":
    uvicorn.run("src.main:src", host="0.0.0.0", port=8000, reload=True)
