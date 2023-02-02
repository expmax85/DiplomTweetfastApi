import os
from pathlib import Path

from pydantic import BaseSettings


BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
    STATIC_DIR = os.path.join(str(BASE_DIR), 'static')
    UPLOADS_DIR = os.path.join(str(STATIC_DIR), 'images')


settings = Settings()
