from pydantic import BaseModel


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    pid: list = None

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

    class Config:
        orm_mode = True


class TokenBase(BaseModel):
    api_key: str


class TokenCreate(TokenBase):
    pass


class Token(TokenBase):
    id: int

    class Config:
        orm_mode = True
