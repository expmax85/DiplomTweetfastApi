from fastapi import Depends

from src.models.models import Tweet, User, Token
from src.models.models import Like
from src.models.models import Media
from abc import abstractmethod
from typing import TypeAlias, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.engine import Row

from src.database.database import AbstractAsyncSession, get_db
from src.models import schemas

ModelType: TypeAlias = Union[Tweet, User]
CreateSchema: TypeAlias = Union[schemas.TweetCreate, schemas.UserCreate]
UpdateSchema: TypeAlias = Union[schemas.UserUpdate, schemas.TweetUpdate]


class BaseAction:
    @abstractmethod
    def __init__(self, model: type[ModelType], db: AbstractAsyncSession):
        self.model = model
        self.db = db

    async def create(self, obj_in: CreateSchema, **kwargs) -> ModelType:
        async with self.db as db:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data, **kwargs)
            db.session.add(db_obj)
        return db_obj

    async def update(self, id_obj: int, obj_data: UpdateSchema) -> ModelType | None:
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
        return True

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        async with self.db as db:
            result = await db.session.execute(
                select(self.model).offset(skip).limit(limit)
            )
        return result.scalars().all()

    async def get(self, id_obj: int) -> ModelType | None:
        async with self.db as db:
            result = await db.session.execute(
                select(self.model).filter(self.model.id == id_obj)
            )
        return result.scalars().first()

    def serialize(self, obj: ModelType | Row) -> dict:
        return jsonable_encoder(obj)


class TweetAction(BaseAction):

    def __init__(self, db: AbstractAsyncSession):
        self.model = Tweet
        self.db = db

    async def create_like(self, user_id: int, tweet_id: int) -> None:
        async with self.db as db:
            like = Like(tweet_id=tweet_id, user_id=user_id)
            db.add(like)

    async def remove_like(self, user_id: int, tweet_id: int) -> None:
        async with self.db as db:
            like = db.query(Like).filter(Like.user_id == user_id,
                                         Like.tweet_id == tweet_id).first()
            db.delete(like)


class UserAction(BaseAction):

    def __init__(self, db: AbstractAsyncSession):
        self.model = User
        self.db = db

    async def get_user_by_api_key(self, api_key: str) -> User:
        async with self.db as db:
            q = select(User).join(Token, Token.user_id == User.id).where(Token.api_key == api_key)
            result = await db.session.execute(q)
        user = result.scalars().first()
        return user

    async def add_follow(self, user, user_id):
        # followed_user = await self.get(id_obj=user_id)
        async with self.db as db:
            followed_user = await db.session.execute(
                select(self.model).filter(self.model.id == user_id)
            )
            user.follow(followed_user)
            db.session.add(user)



async def create_image(file: str, db: AbstractAsyncSession = get_db()) -> Media:
    async with db:
        db_obj = Media(image=file)
        db.session.add(db_obj)
    return db_obj


def get_tweet_service(db: AbstractAsyncSession = Depends(get_db)):
    return TweetAction(db=db)


def get_user_service(db: AbstractAsyncSession = Depends(get_db)):
    return UserAction(db=db)
# users_orm = UserAction()
