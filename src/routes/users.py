from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from src.database import UserAction, get_user_service
from src.models import schemas, User
from src.routes.tokens import get_current_active_user

router = APIRouter()


@router.post("/users/{user_id}/follow", response_model=schemas.Success)
async def add_follow(user_id: int, user_service: UserAction = Depends(get_user_service),
                     user: User = Depends(get_current_active_user)):
    await user_service.add_follow(user, user_id)
    return {"result": True}


@router.delete("/users/{user_id}/follow", response_model=schemas.Success)
async def remove_follow(user_id: int, user_service: UserAction = Depends(get_user_service),
                        user: User = Depends(get_current_active_user)):
    await user_service.unfollow(user, user_id)
    return {"result": True}


@router.get("/users/me", response_model=schemas.UserInfo)
async def get_self_info(user: User = Depends(get_current_active_user)):
    if not user:
        return JSONResponse({"result": False, "error_type": "Unauthorized", "error_message": "User has no registered"},
                            status_code=403)
    return JSONResponse({"result": True, "user": {"id": user.id, "name": user.name,
                                                  "followers": [usr.to_dict() for usr in user.followers_],
                                                  "following": [usr.to_dict() for usr in user.followed]}},
                        status_code=200)


@router.get("/users/{user_id}", response_model=schemas.UserInfo)
async def get_user_info(user_id: int, user_service: UserAction = Depends(get_user_service)):
    user = await user_service.get(id_obj=user_id)
    return JSONResponse({"result": True, "user": {"id": user.id, "name": user.name,
                                                  "followers": [usr.to_dict() for usr in user.followers_],
                                                  "following": [usr.to_dict() for usr in user.followed]}},
                        status_code=200)
