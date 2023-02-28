import asyncio
import base64
import time

from celery import Celery
from src.config import settings

from .utils import remove_files_from_disk, write_to_disk

celery_app = Celery(__name__)
celery_app.conf.broker_url = settings.CELERY_BROKER_URL


@celery_app.task(name="load_file")
def load_file(data: str, filename: str) -> dict:
    if settings.App.CREATE_TEST_USERS:
        time.sleep(15)
    decoded_contents = base64.b64decode(data)
    asyncio.run(write_to_disk(decoded_contents, filename))
    return {"result": "File uploading to server"}


@celery_app.task(name="remove_files")
def remove_files(data: list[str]):
    asyncio.run(remove_files_from_disk(data))
    return {"result": "All files was removed"}
