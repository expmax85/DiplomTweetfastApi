from pydantic import BaseModel, Field


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


class TweetBase(BaseModel):
    content: str = Field(alias='tweet_data')


class TweetCreate(TweetBase):
    pass


class TweetUpdate(TweetBase):
    pass


class Tweet(TweetBase):
    id: int
    likes: list = []
    author: User
    attachments: list = Field([], alias='images')


    class Config:
        orm_mode = True


class Tweets(BaseModel):
    result: bool = True
    tweets: list[Tweet]


class TweetSuccess(BaseModel):
    result: bool = True
    tweet_id: int


class Success(BaseModel):
    result: bool = True
