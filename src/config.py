from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MYSQL_USER: str = "user"
    MYSQL_PASSWORD: str = "password"
    MYSQL_HOST: str = "db"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "delivery_service"
    REDIS_URL: str = "redis://redis:6379"
    # Можно добавить и другие настройки, например, для внешних API и т.д.

    class Config:
        env_file = ".env"  # если нужен файл с переменными окружения

settings = Settings()

