from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext

from src.models import schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def to_json(data: schemas.TweetsSerialize) -> dict:
    result = jsonable_encoder(data)
    for item in result['tweets']:
        item['content'] = item.pop('tweet_data')
        item['attachments'] = [i['image'] for i in item['attachments']]
    return result
