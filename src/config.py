import os
from pathlib import Path

from pydantic import BaseSettings

BASE_DIR = Path(__file__).parent.parent

env_path = os.path.join(BASE_DIR, os.getenv("CONFIG_FILE", ".env.default"))


class App(BaseSettings):
    DEBUG: bool
    SENTRY_DSN: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    TITLE: str = "Tweetter Clone"
    DESCRIPTION: str = "Microblogs service"
    VERSION: str = "1.0"
    COUNT_IMAGES: int = 5
    CREATE_TEST_USERS: bool = False
    ALLOWED_FILES: list[str] = ["png", "jpg", "jpeg"]
    MAX_IMG_SIZE_MB: int = 3
    CACHE_TWEET_PREFIX: str = "tweets"
    CACHE_USER_PREFIX: str = "users"
    ORIGINS: list[str] = []

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
    RABBIT_USER: str
    RABBIT_PASSWORD: str

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
    CACHE_URL: str = f"redis://{Redis.REDIS_HOST}"
    CELERY_BROKER_URL: str = f"amqp://{RabbitMQ.RABBIT_USER}:{RabbitMQ.RABBIT_PASSWORD}@{RabbitMQ.RABBIT_HOST}/"

    STATIC_DIR = os.path.join(str(BASE_DIR), "static")
    UPLOADS_DIR = os.path.join("static", "images")
    MAX_SIZE = App.MAX_IMG_SIZE_MB * 1024**2


settings = Settings()
