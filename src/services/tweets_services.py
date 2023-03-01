import base64
import os
import uuid

from fastapi import Depends, File
from fastapi.encoders import jsonable_encoder

from src.cache import RedisCache, get_cache
from src.celery.celery_app import load_file, remove_files
from src.config import settings
from src.database import MediaAction, TweetAction, get_media_action, get_tweet_action
from src.exceptions import (
    CreateTweetError,
    NotAllowedError,
    SizeFileError,
    TweetNotExist,
    WrongFileError,
)
from src.models import User, schemas

from .base_service import Service
from .utils import _to_json, key_gen


class TweetService(Service):
    def __init__(
        self,
        main_action: TweetAction,
        media_action: MediaAction,
        cache: RedisCache,
        cache_key_prefix: str,
    ) -> None:
        self.action = main_action
        self.media_action = media_action
        self.success_response = schemas.Success().dict()
        self.cache = cache
        self.cache_key_prefix = cache_key_prefix

    async def create(self, data: schemas.TweetCreate, user_id: int) -> dict:
        obj_in_data = jsonable_encoder(data)
        if len(obj_in_data.get("tweet_media_ids")):
            if not await self._check_exist_media(obj_in_data.get("tweet_media_ids")):
                if settings.App.CREATE_TEST_USERS:
                    raise Exception
                else:
                    raise CreateTweetError
        tweet = await self.action.create(data=obj_in_data, user_id=user_id)
        if data.tweet_media_ids:
            await self.media_action.update(tweet=tweet)
        await self.cache.set_cache(
            data=jsonable_encoder(tweet), key=key_gen(self.cache_key_prefix, tweet.id)
        )
        return schemas.TweetSuccess(tweet_id=tweet.id).dict()

    async def get_all(self, skip: int, limit: int) -> dict:
        result = await self.cache.get_cache(key=key_gen(self.cache_key_prefix))
        if not result:
            tweets = await self.action.get_all(skip=skip, limit=limit)
            tweets = schemas.TweetsSerialize(tweets=tweets)
            result = _to_json(tweets.dict())
            await self.cache.set_cache(data=result, key=key_gen(self.cache_key_prefix))
        return jsonable_encoder(result)

    async def get(self, tweet_id: int) -> list | dict | None:
        result = await self.cache.get_cache(
            key=key_gen(self.cache_key_prefix, tweet_id)
        )
        if not result:
            tweet = await self.action.get(tweet_id=tweet_id)
            result = jsonable_encoder(tweet)
            await self.cache.set_cache(
                data=result,
                key=key_gen(self.cache_key_prefix, tweet_id),
            )
        return result

    async def update(self, tweet_id: int, data: schemas.TweetUpdate) -> dict | None:
        updated_tweet = await self.action.update(tweet_id=tweet_id, data=data)
        await self.cache.delete_cache(key=key_gen(self.cache_key_prefix, tweet_id))
        return updated_tweet

    async def remove(self, tweet_id: int, user: "User"):
        tweet = await self.action.get(tweet_id=tweet_id)
        if not tweet:
            raise TweetNotExist
        elif not tweet.is_author(user):
            raise NotAllowedError
        if tweet.attachments and len(tweet.attachments):
            del_list = [item.image for item in tweet.attachments]
            await self.media_action.remove(media_ids=tweet.tweet_media_ids)
            remove_files.delay(data=del_list)
        await self.action.remove(tweet_id=tweet_id)
        await self.cache.delete_cache(key=key_gen(self.cache_key_prefix))
        await self.cache.delete_cache(key=key_gen(self.cache_key_prefix, tweet_id))
        return self.success_response

    async def add_media(self, file: File) -> dict:
        f_type = file.filename.split(".")[-1]
        if f_type not in settings.App.ALLOWED_FILES:
            raise WrongFileError
        elif file.size > settings.MAX_SIZE:
            raise SizeFileError
        filename = ".".join([str(uuid.uuid4()), f_type])
        path = os.path.join(settings.UPLOADS_DIR, filename)
        image = await self.media_action.create(path=path)

        content = await file.read()
        encoded_contents = base64.b64encode(content).decode("utf-8")
        load_file.delay(data=encoded_contents, filename=path)
        return schemas.MediaSuccess(media_id=image.id).dict()

    async def _check_exist_media(self, media_ids: list[int]) -> bool:
        if len(media_ids) > settings.App.COUNT_IMAGES:
            raise CreateTweetError
        medias = await self.media_action.get(media_ids=media_ids)
        return len(medias) == len(media_ids)

    async def create_like(self, tweet_id: int, user_id: int) -> dict:
        await self.action.create_like(tweet_id=tweet_id, user_id=user_id)
        if not await self.action.check_like(user_id=user_id, tweet_id=tweet_id):
            raise TweetNotExist
        await self.cache.delete_cache(key=key_gen(self.cache_key_prefix))
        await self.cache.delete_cache(key=key_gen(self.cache_key_prefix, tweet_id))
        return self.success_response

    async def remove_like(self, tweet_id: int, user_id: int) -> dict:
        if not await self.action.check_like(user_id=user_id, tweet_id=tweet_id):
            raise TweetNotExist
        await self.action.remove_like(tweet_id=tweet_id, user_id=user_id)
        await self.cache.delete_cache(key=key_gen(self.cache_key_prefix))
        await self.cache.delete_cache(key=key_gen(self.cache_key_prefix, tweet_id))
        return self.success_response


def get_tweet_service(
    action: TweetAction = Depends(get_tweet_action),
    media_action: MediaAction = Depends(get_media_action),
    cache: RedisCache = Depends(get_cache),
) -> TweetService:
    return TweetService(
        main_action=action,
        media_action=media_action,
        cache=cache,
        cache_key_prefix=settings.App.CACHE_TWEET_PREFIX,
    )
