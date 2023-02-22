from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import FlushError
from starlette.responses import JSONResponse

from src.database import UserAction, get_user_action
from src.exceptions import UserNotExist
from src.models import schemas, User
from .base_service import Service


class UserService(Service):

    def __init__(self, main_action: UserAction) -> None:
        self.action = main_action
        self.success_response = schemas.Success().dict()

    async def create(self, data: schemas.UserCreate) -> dict:
        user = await self.action.create(data=data)
        return self.success_response

    async def remove(self, user_id: int) -> dict:
        await self.action.remove(user_id=user_id)
        return self.success_response

    async def get_all(self, skip: int, limit: int) -> dict:
        users = await self.action.get_all(skip=skip, limit=limit)
        return jsonable_encoder(users)

    async def get(self, user_id: int) -> JSONResponse:
        if not (user := await self.action.get(user_id=user_id)):
            raise UserNotExist
        return JSONResponse({"result": True, "user": {"id": user.id, "name": user.name,
                                                      "followers": [usr.to_dict() for usr in user.followers],
                                                      "following": [usr.to_dict() for usr in user.followed]}},
                            status_code=200)

    async def add_follow(self, user: User, followed_id: int) -> dict:
        try:
            await self.action.add_follow(user=user, followed_id=followed_id)
        except InvalidRequestError:
            return self.success_response
        except FlushError:
            raise UserNotExist
        return self.success_response

    async def remove_follow(self, user: User, unfollowed_id: int) -> dict:
        try:
            await self.action.unfollow(user=user, unfollowed_id=unfollowed_id)
        except ValueError:
            return self.success_response
        except TypeError:
            raise UserNotExist
        return self.success_response


def get_user_service(main_action: UserAction = Depends(get_user_action)) -> UserService:
    return UserService(main_action=main_action)
