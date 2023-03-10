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


class SizeImgError(ErrorBase):
    class Config:
        schema_extra = {
            "example": {
                "result": False,
                "error_type": "UploadImageError",
                "error_message": "File too big",
            }
        }


class FileNotImgError(ErrorBase):
    class Config:
        schema_extra = {
            "example": {
                "result": False,
                "error_type": "UploadImageError",
                "error_message": "Wrong format file",
            }
        }


def get_response_scheme(model: type[BaseModel], description: str | None = None):
    if not description:
        description = model.__name__
    return {"model": model, "description": description}
