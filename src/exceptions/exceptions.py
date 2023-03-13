__all__ = (
    "BaseCustomExc",
    "CreateTweetError",
    "UnAuthorizedError",
    "UserNotExist",
    "TweetNotExist",
    "NotAllowedError",
    "InactiveUserError",
    "SizeFileError",
    "WrongFileError",
)


class BaseCustomExc(Exception):
    result: bool = False
    status_code: int = 400
    error_type = "Error"
    error_message = "Some trouble"


class ObjectNotExist(BaseCustomExc):
    status_code = 404
    error_type = "NotExistError"


class UploadImgError(BaseCustomExc):
    status_code = 400
    error_type = "UploadImageError"


class CreateTweetError(BaseCustomExc):
    status_code = 409
    error_type = "CreateError"
    error_message = "Conflict with images content"


class UnAuthorizedError(BaseCustomExc):
    status_code = 401
    error_type = "AuthorizedError"
    error_message = "Not authorized"


class UserNotExist(ObjectNotExist):
    error_message = "User not registered"


class TweetNotExist(ObjectNotExist):
    error_message = "Tweet not exist"


class NotAllowedError(BaseCustomExc):
    status_code = 403
    error_type = "NotAllowedError"
    error_message = "You are not author this message"


class InactiveUserError(BaseCustomExc):
    status_code = 403
    error_type = "InactiveUserError"
    error_message = "This user is inactive. Please write to administration"


class SizeFileError(UploadImgError):
    error_message = "File too big"


class WrongFileError(UploadImgError):
    error_message = "Wrong format file"
