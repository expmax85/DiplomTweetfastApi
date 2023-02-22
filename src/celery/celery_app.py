import asyncio

from celery import Celery
from src.config import settings
from src.celery.utils import write_to_disk

celery_app = Celery(__name__)
celery_app.conf.broker_url = settings.CELERY_BROKER_URL
celery_app.conf.result_backend = settings.CELERY_BACKEND_URL


@celery_app.task(name="load_image")
def load_image(data: bytes, filename: str) -> dict:
    asyncio.run(write_to_disk(data, filename))
    return {"result": "File uploading to server"}


@celery_app.task(name='remove_images')
def remove_imgs(data: list[str]):
    asyncio.run(remove_imgs(data))
    return {"result": "All files was removed"}
