import asyncio
import base64

from celery import Celery
from src.config import settings
from .utils import write_to_disk, remove_files_from_disk

celery_app = Celery(__name__)
celery_app.conf.broker_url = settings.CELERY_BROKER_URL


@celery_app.task(name="load_file")
def load_file(data: str, filename: str) -> dict:
    decoded_contents = base64.b64decode(data)
    asyncio.run(write_to_disk(decoded_contents, filename))
    return {"result": "File uploading to server"}


@celery_app.task(name='remove_files')
def remove_files(data: list[str]):
    asyncio.run(remove_files_from_disk(data))
    return {"result": "All files was removed"}
