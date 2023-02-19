from pydantic import BaseModel
from pydantic import Field


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
    tweet_media_ids: list[int] = Field(None)


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


class TweetResponse(BaseModel):
    id: int
    tweet_data: str
    attachments: list[Media]
    author: Author
    likes: list = []

    class Config:
        orm_mode = True


class TweetsSerialize(BaseModel):
    tweets: list[TweetResponse]

    class Config:
        orm_mode = True


class TweetSuccess(BaseModel):
    result: bool = True
    tweet_id: int


class Success(BaseModel):
    result: bool = True


class MediaCreate(BaseModel):
    result: bool
    media_id: int
