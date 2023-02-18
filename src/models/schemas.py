from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pydantic import Field


class Like(BaseModel):
    user_id: int


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


class Author(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class TweetBase(BaseModel):
    tweet_data: str


class TweetCreate(TweetBase):
    pass


class TweetUpdate(TweetBase):
    pass


class Tweet(TweetBase):
    id: int
    likes: list = []
    author: Author
    attachments: list = Field([], alias='images')

    tweet_data: str

    class Config:
        orm_mode = True


class Media(BaseModel):
    image: str

    class Config:
        orm_mode = True


class TweetSerilize(BaseModel):
    id: int
    content: str = Field(..., alias='tweet_data')
    attachments: list[Media]
    author: Author
    likes: list = []

    class Config:
        orm_mode = True


class TweetResponse(BaseModel):
    id: int
    content: str = Field(..., alias='tweet_data')
    attachments: list[Media]
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


class MediaCreate(BaseModel):
    file: str
