from pydantic import BaseModel, Field


class Success(BaseModel):
    result: bool = True

    class Config:
        schema_extra = {"example": {"result": True}}


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class User(UserBase):
    id: int
    followers: list = []
    following: list = Field([], alias="followed")

    class Config:
        orm_mode = True


class UserInfo(Success):
    user: User

    class Config:
        schema_extra = {
            "example": {
                "result": True,
                "user": {
                    "id": 1,
                    "name": "John",
                    "followers": [],
                    "following": [],
                },
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class Author(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class TweetBase(BaseModel):
    tweet_data: str


class TweetCreate(TweetBase):
    tweet_media_ids: list[int] = Field(None)

    class Config:
        schema_extra = {
            "example": {
                "tweet_data": "Test tweet",
                "tweet_media_ids": [],
            }
        }


class TweetUpdate(TweetBase):
    pass


class Media(BaseModel):
    image: str

    class Config:
        orm_mode = True


class Tweet(BaseModel):
    id: int
    content: str = Field(..., alias="tweet_data")
    attachments: list[Media]
    author: Author
    likes: list = []

    class Config:
        orm_mode = True


class TweetsSerialize(BaseModel):
    tweets: list["Tweet"]

    class Config:
        orm_mode = True


class TweetResponse(BaseModel):
    id: int
    content: str
    attachments: list[str]
    author: dict
    likes: list = []

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "content": "Test tweet",
                "attachments": [],
                "author": {"id": 1, "name": "John"},
                "likes": [],
            }
        }


class TweetsResponse(BaseModel):
    tweets: list[TweetResponse]


class TweetSuccess(Success):
    tweet_id: int

    class Config:
        schema_extra = {
            "example": {
                "result": True,
                "tweet_id": 1,
            }
        }


class MediaSuccess(Success):
    media_id: int

    class Config:
        schema_extra = {
            "example": {
                "result": True,
                "media_id": 1,
            }
        }
