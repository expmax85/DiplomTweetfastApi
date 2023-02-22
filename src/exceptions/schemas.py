from typing import Type

from pydantic import BaseModel


class ErrorBase(BaseModel):
    result: bool = False
    error_type: str
    error_message: str


class Unauthorized(ErrorBase):
    class Config:
        schema_extra = {
            "example": {
                "result": False,
                "error_type": "AuthorizedError",
                "error_message": "Not authorized",
            }
        }


class UserNotExist(ErrorBase):
    class Config:
        schema_extra = {
            "example": {
                "result": False,
                "error_type": "NotExistError",
                "error_message": "User not registered",
            }
        }


class TweetNotExist(ErrorBase):
    class Config:
        schema_extra = {
            "example": {
                "result": False,
                "error_type": "NotExistError",
                "error_message": "Tweet not exist",
            }
        }


class NotAllowedError(ErrorBase):
    class Config:
        schema_extra = {
            "example": {
                "result": False,
                "error_type": "NotAllowedError",
                "error_message": "You are not author this message",
            }
        }


class InActiveUserError(ErrorBase):
    class Config:
        schema_extra = {
            "example": {
                "result": False,
                "error_type": "InactiveUserError",
                "error_message": "This user is inactive. Please write to administration",
            }
        }


class CreateTweetError(ErrorBase):
    class Config:
        schema_extra = {
            "example": {
                "result": False,
                "error_type": "CreateError",
                "error_message": "Conflict with images content",
            }
        }


def get_response_scheme(model: Type[BaseModel], description: str = None):
    if not description:
        description = model.__name__
    return {"model": model, "description": description}
