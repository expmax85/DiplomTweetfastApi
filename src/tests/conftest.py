import asyncio
from collections.abc import Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from src.api import app_api
from src.config import settings
from src.database import get_db, SQLSession, UserAction
from src.models import User, Token, Tweet, Like
from src.models.utils import get_password_hash
from src.routes.tokens import get_current_active_user


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def init_test_data():
    async with get_db() as db:
        user_orm = UserAction(db=db)
        users = await user_orm.get_all()
        if len(users) < 1:
            users = [User(name='John', hashed_password=get_password_hash('123456'), token=Token(api_key='test')),
                     User(name="Mike",
                          hashed_password=get_password_hash('123456'))
                     ]
            tweets = [
                Tweet(tweet_data="Test tweet by John", author=users[0]),
                Tweet(tweet_data="Some test data", author=users[1])
            ]
            db.session.add_all(users)
            db.session.add_all(tweets)
            await db.session.commit()
            like = Like(user_id=users[1].id, tweet_id=tweets[0].id)
            db.session.add(like)


@pytest_asyncio.fixture
async def test_app(init_test_data):
    engine = create_async_engine(settings.DATABASE_URL)
    conn = await engine.connect()
    trans = await conn.begin()
    session = AsyncSession(bind=conn, expire_on_commit=False)
    await init_test_data

    async def get_user():
        user_orm = UserAction(db=SQLSession(session=session))
        usr = await user_orm.get_user_by_api_key(api_key='test')
        return usr

    async def get_test_db():
        try:
            yield SQLSession(session=session)
        finally:
            await session.close()

    app_api.dependency_overrides[get_db] = get_test_db
    app_api.dependency_overrides[get_current_active_user] = get_user
    try:
        async with AsyncClient(app=app_api, base_url="http://test.io") as client:
            yield client
    finally:
        await session.close()
        await trans.rollback()
        await conn.close()
