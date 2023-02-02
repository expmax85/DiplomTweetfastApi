from pydantic import BaseModel, Field


class Like(BaseModel):
    user_id: int
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class User(UserBase):
    id: int
    followers: list = []
    following: list = Field([], alias='followed')

    class Config:
        orm_mode = True


class UserInfo(BaseModel):
    result: bool = True
    user: User


class TweetBase(BaseModel):
    tweet_data: str


class TweetCreate(TweetBase):
    pass


class TweetUpdate(TweetBase):
    pass


class Tweet(TweetBase):
    id: int
    likes: list = []
    author: User
    attachments: list = Field([], alias='images')

    tweet_data: str

    class Config:
        orm_mode = True


class Author(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class TweetResponse(BaseModel):
    id: int
    content: str = Field(..., alias='tweet_data')
    attachments: list = []
    author: Author
    likes: list = []

    class Config:
        orm_mode = True


class Tweets(BaseModel):
    result: bool = True
    tweets: list[TweetResponse]

    class Config:
        orm_mode = True


class TweetSuccess(BaseModel):
    result: bool = True
    tweet_id: int


class Success(BaseModel):
    result: bool = True


def to_json(data: dict):
    print(data)
    result = jsonable_encoder(data)
    for item in result['tweets']:
        item['content'] = item.pop('tweet_data')
    return result


class MediaCreate(BaseModel):
    file: str
