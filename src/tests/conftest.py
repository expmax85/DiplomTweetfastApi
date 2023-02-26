import asyncio
from collections.abc import Generator

import pytest
import pytest_asyncio
from fastapi import Depends
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.api import app_api
from src.cache import get_cache
from src.cache.base_cache_service import AbstractCache
from src.config import settings
from src.database import SQLSession, UserAction, get_db
from src.exceptions import UnAuthorizedError
from src.models import Like, Token, Tweet, User
from src.models.utils import get_password_hash
from src.routes.tokens import get_current_active_user, oauth2_scheme


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def init_test_data(db):
    async with db as db:
        user_orm = UserAction(db=db)
        users = await user_orm.get_all()
        if len(users) < 1:
            users = [
                User(
                    name="John",
                    hashed_password=get_password_hash("123456"),
                    token=Token(api_key="test"),
                ),
                User(name="Mike", hashed_password=get_password_hash("123456")),
            ]
            tweets = [
                Tweet(tweet_data="Test tweet by John", author=users[0]),
                Tweet(tweet_data="Some test data", author=users[1]),
            ]
            db.session.add_all(users)
            db.session.add_all(tweets)
            await db.session.commit()
            like = Like(user_id=users[1].id, tweet_id=tweets[0].id)
            db.session.add(like)


class DisableCache(AbstractCache):
    def __init__(self, nocache=None):
        self.cache = nocache

    async def get_cache(self, key):
        return None

    async def set_cache(self, data, key):
        return data

    async def delete_cache(self, key):
        pass

    async def delete_many(self, key_parent: str):
        pass


def get_no_cache() -> DisableCache:
    return DisableCache()


@pytest_asyncio.fixture
async def test_app():
    engine = create_async_engine(settings.DATABASE_URL)
    conn = await engine.connect()
    trans = await conn.begin()
    session = AsyncSession(bind=conn, expire_on_commit=False)
    await init_test_data(db=SQLSession(session=session))

    async def get_user(token: str = Depends(oauth2_scheme)):
        user_orm = UserAction(db=SQLSession(session=session))
        if "api-key" in token and (
            usr := await user_orm.get_user_by_api_key(api_key=token[0])
        ):
            return usr
        raise UnAuthorizedError

    async def get_test_db():
        try:
            yield SQLSession(session=session)
        finally:
            await session.close()

    app_api.dependency_overrides[get_cache] = get_no_cache
    app_api.dependency_overrides[get_db] = get_test_db
    app_api.dependency_overrides[get_current_active_user] = get_user
    try:
        async with AsyncClient(app=app_api, base_url="http://test.io") as client:
            yield client
    finally:
        await session.close()
        await trans.rollback()
        await conn.close()
