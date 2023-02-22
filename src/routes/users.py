from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from src.services import UserService, get_user_service
from src.models import schemas, User
from src.exceptions import schemas as exc_schemes
from src.exceptions import get_response_scheme
from src.routes.tokens import get_current_active_user

router = APIRouter(tags=['Users'], responses={401: get_response_scheme(model=exc_schemes.Unauthorized),
                                              403: get_response_scheme(model=exc_schemes.InActiveUserError)})


@router.post("/users/{user_id}/follow", response_model=schemas.Success,
             status_code=status.HTTP_201_CREATED,
             responses={404: get_response_scheme(model=exc_schemes.UserNotExist)})
async def add_follow(user_id: int, user_service: UserService = Depends(get_user_service),
                     user: User = Depends(get_current_active_user)):
    """ Adding user to followed.

     - ***user_id*** - id by user, who need to add in followed"""
    return await user_service.add_follow(user=user, followed_id=user_id)


@router.delete("/users/{user_id}/follow", response_model=schemas.Success,
               status_code=status.HTTP_202_ACCEPTED,
               responses={404: get_response_scheme(model=exc_schemes.UserNotExist)})
async def remove_follow(user_id: int, user_service: UserService = Depends(get_user_service),
                        user: User = Depends(get_current_active_user)):
    """ Removing user from followed.

     - ***user_id*** - id by user, who need to remove from followed"""
    return await user_service.remove_follow(user=user, unfollowed_id=user_id)


@router.get("/users/me", response_model=schemas.UserInfo)
async def get_self_info(user: User = Depends(get_current_active_user)):
    """ Get userinfo about self."""
    return JSONResponse({"result": True, "user": {"id": user.id, "name": user.name,
                                                  "followers": [usr.to_dict() for usr in user.followers],
                                                  "following": [usr.to_dict() for usr in user.followed]}},
                        status_code=200)


@router.get("/users/{user_id}", response_model=schemas.UserInfo,
            dependencies=[Depends(get_current_active_user)],
            responses={404: get_response_scheme(model=exc_schemes.UserNotExist)})
async def get_user_info(user_id: int, user_service: UserService = Depends(get_user_service)):
    """ Get userinfo bu his id.

     - ***user_id*** - id by user"""
    return await user_service.get(user_id=user_id)
