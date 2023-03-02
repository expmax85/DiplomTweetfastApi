from collections.abc import Sequence

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Row, delete, select, update, func
from sqlalchemy.orm import selectinload

from src.models import Like, Media, Token, Tweet, User, schemas

from .abstracts import AbstractAction
from .database import SQLSession, get_db

__all__ = (
    "get_user_action",
    "get_tweet_action",
    "get_media_action",
    "TweetAction",
    "UserAction",
    "MediaAction",
)

from ..models.models import Follower


class TweetAction(AbstractAction):
    def __init__(self, db: SQLSession) -> None:
        self.model = Tweet
        self.db = db

    async def create(self, data: dict, **kwargs) -> Tweet:
        async with self.db as db:
            db_obj = self.model(**data, **kwargs)
            db.session.add(db_obj)
        return db_obj

    async def update(self, tweet_id: int, data: schemas.TweetUpdate) -> Tweet | None:
        if updated_obj := await self.get(tweet_id=tweet_id):
            async with self.db as db:
                for key, value in data.dict(exclude_unset=True).items():
                    setattr(updated_obj, key, value)
                db.session.add(updated_obj)
        return updated_obj

    async def remove(self, tweet_id: int) -> bool:
        stmt = (
            delete(self.model)
            .options(
                selectinload(self.model.attachments),
                selectinload(self.model.author),
                selectinload(self.model.likes),
            )
            .where(self.model.id == tweet_id)
        )
        stmt_like = delete(Like).where(Like.tweet_id == tweet_id)
        async with self.db as db:
            await db.session.execute(stmt_like)
            await db.session.execute(stmt)
        return True

    def _stmt_get(self) -> "select":
        return select(self.model).options(
            selectinload(self.model.attachments),
            selectinload(self.model.author),
            selectinload(self.model.likes),
        )

    async def get(self, tweet_id: int) -> Tweet | None:
        stmt = self._stmt_get().where(self.model.id == tweet_id)
        async with self.db as db:
            result = await db.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Row]:
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
                select(Like).filter(Like.user_id == user_id, Like.tweet_id == tweet_id)
            )
            like = query.scalars().first()
            await db.session.delete(like)

    async def check_like(self, user_id: int, tweet_id: int) -> bool:
        stmt = select(Like).where(Like.user_id == user_id, Like.tweet_id == tweet_id)
        async with self.db as db:
            result = await db.session.execute(stmt)
        return bool(result.scalars().all())

    async def rss_popular(self, user_id: int) -> Sequence[Row]:
        stmt = self._stmt_get()\
            .join(Follower, Follower.follower_id == user_id)\
            .join(Like, Like.tweet_id == self.model.id)\
            .where(self.model.user_id == Follower.followed_id)\
            .group_by(self.model.id)\
            .order_by(func.count(self.model.likes).desc())
        async with self.db as db:
            result = await db.session.execute(stmt)
        return result.scalars().all()


class UserAction(AbstractAction):
    def __init__(self, db: SQLSession):
        self.model = User
        self.db = db

    async def create(self, data: schemas.UserCreate, **kwargs) -> User:
        async with self.db as db:
            obj_in_data = jsonable_encoder(data)
            db_obj = self.model(**obj_in_data, **kwargs)
            db.session.add(db_obj)
        return db_obj

    async def update(self, user_id: int, obj_data: schemas.UserUpdate) -> User | None:
        if updated_obj := await self.get(user_id=user_id):
            async with self.db as db:
                for key, value in obj_data.dict(exclude_unset=True).items():
                    setattr(updated_obj, key, value)
                db.session.add(updated_obj)
        return updated_obj

    async def remove(self, user_id: int) -> bool:
        if result := await self.get(user_id=user_id):
            async with self.db as db:
                await db.session.delete(result)
                await db.session.commit()
        return True

    def _stmt_get(self):
        return select(self.model).options(
            selectinload(self.model.followed),
            selectinload(self.model.followers),
            selectinload(self.model.likes),
            selectinload(self.model.tweets),
            selectinload(self.model.likes),
        )

    async def get(self, user_id: int) -> User | None:
        stmt = self._stmt_get().where(self.model.id == user_id)
        async with self.db as db:
            result = await db.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Row]:
        stmt = self._stmt_get().offset(skip).limit(limit)
        async with self.db as db:
            result = await db.session.execute(stmt)
        return result.scalars().all()

    async def get_user_by_api_key(self, api_key: str) -> User:
        stmt = (
            self._stmt_get()
            .join(Token, Token.user_id == User.id)
            .where(Token.api_key == api_key)
        )
        async with self.db as db:
            result = await db.session.execute(stmt)
        user = result.scalars().first()
        return user

    async def get_by_name(self, name: str) -> User:
        stmt = self._stmt_get().where(self.model.name == name)
        async with self.db as db:
            result = await db.session.execute(stmt)
        user = result.scalars().first()
        return user

    async def add_follow(self, user: User, followed_id) -> None:
        stmt = select(self.model).filter(self.model.id == followed_id)
        async with self.db as db:
            result = await db.session.execute(stmt)
            followed_user = result.scalars().first()
            user.follow(followed_user)
            db.session.add(user)
            await db.session.commit()

    async def unfollow(self, user: User, unfollowed_id: int) -> None:
        stmt = self._stmt_get().where(self.model.id == unfollowed_id)
        async with self.db as db:
            result = await db.session.execute(stmt)
            followed_user = result.scalars().first()
            user.unfollow(followed_user)


class MediaAction(AbstractAction):
    def __init__(self, db: SQLSession):
        self.model = Media
        self.db = db

    async def create(self, path: str) -> Media:
        async with self.db as db:
            image = self.model(image=path)
            db.session.add(image)
        return image

    async def update(self, tweet: Tweet) -> None:
        stmt = (
            update(self.model)
            .where(self.model.id.in_(tweet.tweet_media_ids))
            .values({"tweet_id": tweet.id})
        )
        async with self.db as db:
            await db.session.execute(stmt)

    async def remove(self, media_ids: list) -> None:
        stmt = delete(self.model).where(self.model.id.in_(media_ids))
        async with self.db as db:
            await db.session.execute(stmt)

    async def get(self, media_ids: list) -> Sequence[Row]:
        stmt = select(Media.id).where(Media.id.in_(media_ids))
        async with self.db as db:
            result = await db.session.execute(stmt)
        return result.scalars().all()

    async def get_all(self) -> Sequence[Row]:
        async with self.db as db:
            result = await db.session.execute(select(self.model))
        return result.scalars().all()


def get_user_action(db: SQLSession = Depends(get_db)):
    return UserAction(db=db)


def get_media_action(db: SQLSession = Depends(get_db)):
    return MediaAction(db=db)


def get_tweet_action(db: SQLSession = Depends(get_db)):
    return TweetAction(db=db)
