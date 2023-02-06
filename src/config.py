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


class Settings(BaseSettings):
    App: App = App()
    Database: DBconfig = DBconfig()

    DATABASE_URL: str = (
        f"postgresql+asyncpg://{Database.DB_USER}:{Database.DB_PASSWORD}"
        f"@{Database.DB_HOST}/{Database.DB_NAME}"
    )
    STATIC_DIR = os.path.join(str(BASE_DIR), 'static')
    UPLOADS_DIR = os.path.join(str(STATIC_DIR), 'images')


settings = Settings()
