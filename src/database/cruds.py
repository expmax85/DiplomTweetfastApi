from abc import abstractmethod
from typing import TypeAlias, Union

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.models import schemas, Tweet, User
from src.models.models import Like, Token, Media

ModelType: TypeAlias = Union[Tweet, User]
CreateSchema: TypeAlias = Union[schemas.TweetCreate, schemas.UserCreate]
UpdateSchema: TypeAlias = Union[schemas.UserUpdate, schemas.TweetUpdate]


class BaseAction:
    @abstractmethod
    def __init__(self, model: type[ModelType], session: Session):
        self.model = model
        self.session = session

    def create(self, obj_in: CreateSchema, **kwargs) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, **kwargs)
        self.session.add(db_obj)
        return db_obj

    def update(self, id_obj: int, obj_data: UpdateSchema) -> ModelType | None:
        if updated_obj := self.get(id_obj=id_obj):
            for key, value in obj_data.dict(exclude_unset=True).items():
                setattr(updated_obj, key, value)
            self.session.add(updated_obj)
        return updated_obj

    def remove(self, id_obj: int) -> bool:
        if result := self.get(id_obj=id_obj):
            self.session.delete(result)
        return True

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Row]:
        result = self.session.scalars(
            select(self.model).offset(skip).limit(limit).all()
        ).all()
        return result

    def get(self, id_obj: int) -> ModelType | None:
        result = self.session.execute(
            select(self.model).filter(self.model.id == id_obj)
        )
        return result.scalars().first()

    def serialize(self, obj: ModelType | Row) -> dict:
        return jsonable_encoder(obj)


class TweetAction(BaseAction):

    def __init__(self, session):
        self.model = Tweet
        self.session = session

    def create_like(self, user_id: int, tweet_id: int) -> None:
        like = Like(tweet_id=tweet_id, user_id=user_id)
        self.session.add(like)

    def remove_like(self, user_id: int, tweet_id: int) -> None:
        like = self.session.scalars(select(Like).where(Like.user_id == user_id,
                                     Like.tweet_id == tweet_id)).first()
        self.session.delete(like)


class UserAction(BaseAction):

    def __init__(self, session):
        self.model = User
        self.session = session

    def get_user_by_api_key(self, api_key: str) -> User:
        q = select(User).join(Token, Token.user_id == User.id).where(Token.api_key == api_key)
        result = self.session.scalars(q).first()
        # user = result.scalars().first()
        return result

    def add_follow(self, user, user_id):
        # followed_user = await self.get(id_obj=user_id)
        followed_user = self.session.scalars(
            select(self.model).filter(self.model.id == user_id)
        ).first()
        user.follow(followed_user)
        self.session.add(user)


def create_image(file: str, session: Session = Depends(get_db)) -> Media:
    db_obj = Media(image=file)
    session.add(db_obj)
    return db_obj


def get_tweet_service(session: Session = Depends(get_db)):
    return TweetAction(session=session)


def get_user_service(session: Session = Depends(get_db)):
    return UserAction(session=session)
# users_orm = UserAction()
