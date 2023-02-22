import os
import uuid

from fastapi import File, Depends
from fastapi.encoders import jsonable_encoder

from src.config import settings
from src.database import TweetAction, MediaAction, get_tweet_action, get_media_action
from src.exceptions import NotAllowedError, CreateTweetError, TweetNotExist, WrongFileError, SizeFileError
from src.models import schemas, User
from .base_service import Service
from src.celery.celery_app import load_image, remove_imgs


class TweetService(Service):

    def __init__(self, main_action: TweetAction, media_action: MediaAction) -> None:
        self.action = main_action
        self.media_action = media_action
        self.success_response = schemas.Success().dict()

    async def create(self, data: schemas.TweetCreate, user_id: int) -> dict:
        obj_in_data = jsonable_encoder(data)
        if len(obj_in_data.get('tweet_media_ids')):
            if not await self._check_exist_media(obj_in_data.get('tweet_media_ids')):
                raise CreateTweetError
        tweet = await self.action.create(data=obj_in_data, user_id=user_id)
        await self.media_action.update(tweet=tweet)
        return schemas.TweetSuccess(tweet_id=tweet.id).dict()

    async def add_media(self, file: File) -> dict:
        ftype = file.filename.split('.')[-1]
        if ftype not in settings.App.ALLOWED_FILES:
            raise WrongFileError
        elif file.size > settings.MAX_SIZE:
            raise SizeFileError
        filename = ".".join([str(uuid.uuid4()), ftype])
        path = os.path.join(settings.UPLOADS_DIR, filename)
        load_image.delay(data=file.file.read(), filename=path)
        # write_to_disk(file.file.read(), path)
        image = await self.media_action.create(path=path)
        return schemas.MediaSuccess(media_id=image.id).dict()

    async def remove(self, tweet_id: int, user: 'User'):
        tweet = await self.action.get(tweet_id=tweet_id)
        if not tweet:
            raise TweetNotExist
        elif not tweet.is_author(user):
            raise NotAllowedError
        del_list = (item.image for item in tweet.attachments)
        await self.media_action.remove(media_ids=tweet.tweet_media_ids)
        await self.action.remove(tweet_id=tweet_id)
        remove_imgs.delay(data=del_list)
        # await remove_files(del_list=del_list)
        return self.success_response

    async def create_like(self, tweet_id: int, user_id: int) -> dict:
        await self.action.create_like(tweet_id=tweet_id, user_id=user_id)
        if not await self.action.check_like(user_id=user_id, tweet_id=tweet_id):
            raise TweetNotExist
        return self.success_response

    async def remove_like(self, tweet_id: int, user_id: int) -> dict:
        if not await self.action.check_like(user_id=user_id, tweet_id=tweet_id):
            raise TweetNotExist
        await self.action.remove_like(tweet_id=tweet_id, user_id=user_id)
        return self.success_response

    async def get_all(self, skip: int, limit: int) -> dict:
        tweets = await self.action.get_all(skip=skip, limit=limit)
        tweets = schemas.TweetsSerialize(tweets=tweets)
        return self._to_json(tweets.dict())

    async def get(self, tweet_id: int):
        pass

    def _to_json(self, data: dict) -> dict:
        for item in data['tweets']:
            item['attachments'] = [i['image'] for i in item['attachments']]
        return data

    async def _check_exist_media(self, media_ids: list[int]) -> bool:
        if len(media_ids) > settings.App.COUNT_IMAGES:
            raise CreateTweetError
        medias = await self.media_action.get(media_ids=media_ids)
        return len(medias) == len(media_ids)


def get_tweet_service(action: TweetAction = Depends(get_tweet_action),
                      media_action: MediaAction = Depends(get_media_action)) -> TweetService:
    return TweetService(main_action=action, media_action=media_action)
