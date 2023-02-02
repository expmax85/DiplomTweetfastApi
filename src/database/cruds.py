from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pydantic.schema import Generic, TypeVar
from sqlalchemy.orm import Session

from src.models import Base, Tweet, User
from src.models import schemas
from src.models.models import Like
from src.models.models import Media

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    model = None

    def __init__(self, *args, **kwargs):
        if not self.model:
            raise AttributeError('Need to define model')

    def create(self, db: Session, obj_in: CreateSchemaType, **kwargs) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, **kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id_obj: int) -> bool:
        obj = db.query(self.model).get(id_obj)
        db.delete(obj)
        db.commit()
        return True

    def update(self, db: Session, id_obj: int, obj_data: UpdateSchemaType) -> int:
        updated = db.query(self.model).filter(self.model.id == id_obj).update(obj_data.dict(exclude_unset=True))
        db.commit()
        return updated

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> list[tuple]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def get(self, db: Session, id_obj: int) -> ModelType | None:
        return db.query(self.model).filter(self.model.id == id_obj).first()


class TweetAction(BaseCRUD[Tweet, schemas.TweetCreate, schemas.TweetUpdate]):
    model = Tweet

    def create_like(self, db: Session, user_id: int, tweet_id: int) -> None:
        like = Like(tweet_id=tweet_id, user_id=user_id)
        db.add(like)
        db.commit()

    def remove_like(self, db: Session, user_id: int, tweet_id: int) -> None:
        like = db.query(Like).filter(Like.user_id == user_id,
                                     Like.tweet_id == tweet_id).first()
        db.delete(like)
        db.commit()


class UserAction(BaseCRUD[User, schemas.UserCreate, schemas.UserUpdate]):
    model = User


def create_image(db: Session, file: str, tweet_id) -> Media:
    db_obj = Media(image=file, tweet_media_ids=1)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


tweets_orm = TweetAction()
