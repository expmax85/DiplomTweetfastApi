from fastapi import Depends
from sqlalchemy.orm import selectinload

from src.models import schemas
from src.models.models import Tweet, User, Token
from src.models.models import Like
from src.models.models import Media
from abc import abstractmethod, ABC

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, delete
from sqlalchemy.engine import Row

from src.database.database import AbstractAsyncSession, get_db


class AbstractAction(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def create(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def remove(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_all(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError


class TweetAction(AbstractAction):

    def __init__(self, db: AbstractAsyncSession):
        self.model = Tweet
        self.db = db

    async def create(self, obj_in: schemas.TweetCreate, **kwargs) -> Tweet:
        async with self.db as db:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data, **kwargs)
            db.session.add(db_obj)
        return db_obj

    async def update(self, id_obj: int, obj_data: schemas.TweetUpdate) -> Tweet | None:
        if updated_obj := await self.get(id_obj=id_obj):
            async with self.db as db:
                for key, value in obj_data.dict(exclude_unset=True).items():
                    setattr(updated_obj, key, value)
                db.session.add(updated_obj)
        return updated_obj

    async def remove(self, id_obj: int) -> bool:
        if result := await self.get(id_obj=id_obj):
            stmt = delete(Like).where(Like.tweet_id == id_obj)
            async with self.db as db:
                await db.session.execute(stmt)
                await db.session.delete(result)
        return True

    def _stmt_get(self):
        return select(self.model).options(selectinload(self.model.attachments),
                                          selectinload(self.model.author),
                                          selectinload(self.model.likes))

    async def get(self, id_obj: int) -> Tweet | None:
        stmt = self._stmt_get().where(self.model.id == id_obj)
        async with self.db as db:
            result = await db.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Tweet]:
        stmt = self._stmt_get().offset(skip).limit(limit)
        async with self.db as db:
            result = await db.session.execute(stmt)
        return result.scalars().all()

    async def create_like(self, user_id: int, tweet_id: int) -> None:
        async with self.db as db:
            like = Like(tweet_id=tweet_id, user_id=user_id)
            db.session.add(like)

    async def remove_like(self, user_id: int, tweet_id: int) -> None:
        async with self.db as db:
            query = await db.session.execute(
                select(Like)
                .filter(Like.user_id == user_id,
                        Like.tweet_id == tweet_id)
            )
            like = query.scalars().first()
            await db.session.delete(like)

    def serialize(self, obj: Tweet | Row) -> dict:
        return jsonable_encoder(obj)


class UserAction(AbstractAction):

    def __init__(self, db: AbstractAsyncSession):
        self.model = User
        self.db = db

    async def create(self, obj_in: schemas.UserCreate, **kwargs) -> User:
        async with self.db as db:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data, **kwargs)
            db.session.add(db_obj)
        return db_obj

    async def update(self, id_obj: int, obj_data: schemas.UserUpdate) -> User | None:
        if updated_obj := await self.get(id_obj=id_obj):
            async with self.db as db:
                for key, value in obj_data.dict(exclude_unset=True).items():
                    setattr(updated_obj, key, value)
                db.session.add(updated_obj)
        return updated_obj

    async def remove(self, id_obj: int) -> bool:
        if result := await self.get(id_obj=id_obj):

            async with self.db as db:
                await db.session.delete(result)
                await db.session.commit()

        return True

    def _stmt_get(self):
        return select(self.model).options(selectinload(self.model.followed),
                                          selectinload(self.model.followers),
                                          selectinload(self.model.likes),
                                          selectinload(self.model.tweets),
                                          selectinload(self.model.likes))

    async def get(self, id_obj: int) -> User | None:
        stmt = self._stmt_get().where(self.model.id == id_obj)
        async with self.db as db:
            result = await db.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        stmt = self._stmt_get().offset(skip).limit(limit)
        async with self.db as db:
            result = await db.session.execute(stmt)
        return result.scalars().all()

    async def get_user_by_api_key(self, api_key: str) -> User:
        stmt = self._stmt_get().join(Token, Token.user_id == User.id).where(Token.api_key == api_key)
        async with self.db as db:
            result = await db.session.execute(stmt)
        user = result.scalars().first()
        return user

    async def add_follow(self, user: User, user_id) -> None:
        async with self.db as db:
            followed_user = await db.session.execute(
                select(self.model).filter(self.model.id == user_id)
            )
            user.follow(followed_user.scalars().first())
            db.session.add(user)

    async def unfollow(self, user: User, user_id: int) -> None:
        stmt = self._stmt_get().where(self.model.id == user_id)
        async with self.db as db:
            result = await db.session.execute(
                stmt
            )
            followed_user = result.scalars().first()
            user.unfollow(followed_user)


async def create_image(file: str, db: AbstractAsyncSession = get_db()) -> Media:
    async with db:
        db_obj = Media(image=file)
        db.session.add(db_obj)
    return db_obj


def get_tweet_service(db: AbstractAsyncSession = Depends(get_db)):
    return TweetAction(db=db)


def get_user_service(db: AbstractAsyncSession = Depends(get_db)):
    return UserAction(db=db)

