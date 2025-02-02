import uuid
from fastapi import Request, Response
import redis.asyncio as redis

SESSION_COOKIE_NAME = "session_id"
redis_client = None

def get_or_create_session(request: Request, response: Response) -> str:
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(key=SESSION_COOKIE_NAME, value=session_id)
    return session_id

async def init_redis():
    global redis_client
    redis_client = redis.from_url("redis://redis:6379", decode_responses=True)

async def get_exchange_rate():
    rate = await redis_client.get("dollar_rate")
    if rate:
        return float(rate)
    return None

async def set_exchange_rate(rate: float, ttl: int = 300):
    # Параметр ex задаёт время жизни ключа в секундах
    await redis_client.set("dollar_rate", rate, ex=ttl)
