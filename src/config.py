import os
from pathlib import Path

from pydantic import BaseSettings


BASE_DIR = Path(__file__).parent.parent

env_path = os.path.join(BASE_DIR, os.getenv("CONFIG_FILE", ".env.default"))


class App(BaseSettings):
    DEBUG: bool = True
    TITLE: str = "FastAPI"
    DESCRIPTION: str = ""
    VERSION: str = "1.0"

    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    COUNT_IMAGES: int = 5
    CREATE_TEST_USERS: bool = True
    ALLOWED_FILES: list[str] = ['png', 'jpg', 'jpeg']
    MAX_IMG_SIZE_MB: int = 3

    class Config:
        env_file = env_path


class DBconfig(BaseSettings):
    DB_NAME: str
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: int

    class Config:
        env_file: str = env_path


class Redisconfig(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int

    class Config:
        env_file: str = env_path


class RabbitMQ(BaseSettings):
    RABBIT_HOST: str
    RABBIT_PORT: int
    RABBIT_USER: str = "guest"
    RABBIT_PASSWORD: str = "guest"

    class Config:
        env_file: str = env_path


class Settings(BaseSettings):
    App: App = App()
    Database: DBconfig = DBconfig()
    Redis: Redisconfig = Redisconfig()
    RabbitMQ: RabbitMQ = RabbitMQ()

    DATABASE_URL: str = (
        f"postgresql+asyncpg://{Database.DB_USER}:{Database.DB_PASSWORD}"
        f"@{Database.DB_HOST}/{Database.DB_NAME}"
    )
    CELERY_BROKER_URL: str = f"amqp://{RabbitMQ.RABBIT_USER}:{RabbitMQ.RABBIT_PASSWORD}@{RabbitMQ.RABBIT_HOST}/"
    CELERY_BACKEND_URL: str = f"rpc://{Redis.REDIS_HOST}"

    STATIC_DIR = os.path.join(str(BASE_DIR), 'static')
    UPLOADS_DIR = os.path.join('static', 'images')
    MAX_SIZE = App.MAX_IMG_SIZE_MB * 1024**2


settings = Settings()
