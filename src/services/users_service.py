from fastapi import Depends
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import FlushError

from src.database import UserAction, get_user_action
from src.exceptions import UserNotExist
from src.models import schemas, User
from src.cache import RedisCache, get_cache
from src.config import settings
from .base_service import Service
from .utils import key_gen, serialize_user


class UserService(Service):

    def __init__(self, main_action: UserAction,
                 cache: RedisCache, cache_key_prefix: str) -> None:
        self.action = main_action
        self.success_response = schemas.Success().dict()
        self.cache = cache
        self.cache_key_prefix = cache_key_prefix

    async def create(self, data: schemas.UserCreate) -> dict:
        user = await self.action.create(data=data)
        await self.cache.delete_cache(key=key_gen(self.cache_key_prefix))
        return serialize_user(user)

    async def get_all(self, skip: int, limit: int) -> dict:
        if not (result := await self.cache.get_cache(key=key_gen(self.cache_key_prefix))):
            users = await self.action.get_all(skip=skip, limit=limit)
            result = [serialize_user(user) for user in users]
            await self.cache.set_cache(data=result, key=key_gen(self.cache_key_prefix))
        return result

    async def get(self, user_id: int) -> dict:
        if not (result := await self.cache.get_cache(key=key_gen(self.cache_key_prefix, user_id))):
            if not (user := await self.action.get(user_id=user_id)):
                raise UserNotExist
            result = serialize_user(user)
            await self.cache.set_cache(data=result, key=key_gen(self.cache_key_prefix, user_id))
        return result

    async def remove(self, user_id: int) -> dict:
        await self.action.remove(user_id=user_id)
        await self.cache.delete_many(key_parent=self.cache_key_prefix)
        await self.cache.delete_cache(key=key_gen(self.cache_key_prefix))
        return self.success_response

    async def update(self, user_id: int, data: schemas.UserUpdate) -> dict:
        updated_user = await self.action.update(user_id=user_id, obj_data=data)
        await self.cache.delete_cache(key=key_gen(self.cache_key_prefix, user_id))
        await self.cache.delete_cache(key=key_gen(self.cache_key_prefix))
        return serialize_user(updated_user)

    async def add_follow(self, user: User, followed_id: int) -> dict:
        try:
            await self.action.add_follow(user=user, followed_id=followed_id)
            await self.cache.delete_cache(key=key_gen(self.cache_key_prefix, user.id))
            await self.cache.delete_cache(key=key_gen(self.cache_key_prefix, followed_id))
            await self.cache.delete_cache(key=key_gen(self.cache_key_prefix))
        except InvalidRequestError:
            return self.success_response
        except FlushError:
            raise UserNotExist
        return self.success_response

    async def remove_follow(self, user: User, unfollowed_id: int) -> dict:
        try:
            await self.action.unfollow(user=user, unfollowed_id=unfollowed_id)
            await self.cache.delete_cache(key=key_gen(self.cache_key_prefix, user.id))
            await self.cache.delete_cache(key=key_gen(self.cache_key_prefix, unfollowed_id))
            await self.cache.delete_cache(key=key_gen(self.cache_key_prefix))
        except ValueError:
            return self.success_response
        except TypeError:
            raise UserNotExist
        return self.success_response


def get_user_service(main_action: UserAction = Depends(get_user_action),
                     cache: RedisCache = Depends(get_cache)) -> UserService:
    return UserService(main_action=main_action, cache=cache,
                       cache_key_prefix=settings.App.CACHE_TWEET_PREFIX)
