from pprint import pprint

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.database import session, cruds
from src.models import schemas, User, Token

router = APIRouter()


async def get_user(request: Request, db: Session = Depends(session)):
    pprint(dict(request.headers), indent=2)
    api_key = request.headers.get('api-key', 'test')
    token = db.query(Token).filter(Token.api_key == api_key).first()
    return token.user


@router.post("/users/{user_id}/follow", response_model=schemas.Success)
async def add_follow(user_id: int, db: Session = Depends(session), user: User = Depends(get_user)):
    followed_user = cruds.users_orm.get(db=db, id_obj=user_id)
    user.follow(followed_user)
    db.commit()
    db.refresh(user)
    return {"result": True}


@router.delete("/users/{user_id}follow", response_model=schemas.Success)
async def remove_follow(user_id: int, db: Session = Depends(session), user: User = Depends(get_user)):
    followed_user = cruds.users_orm.get(db=db, id_obj=user_id)
    user.unfollow(followed_user)
    db.commit()
    db.refresh(user)
    return {"result": True}


@router.get("/users/me")
async def get_self_info(user: User = Depends(get_user)):
    if not user:
        return JSONResponse({"result": False, "error_type": "Unauthorized", "error_message": "User has no registered"},
                            status_code=403)
    return JSONResponse({"result": True, "user": {"id": user.id, "name": user.name,
                                                  "followers": [usr.to_dict() for usr in user.followers],
                                                  "following": [usr.to_dict() for usr in user.followed]}},
                        status_code=200)


@router.get("/users/{user_id}")
async def get_user_info(user_id: int, db: Session = Depends(session)):
    user = cruds.users_orm.get(db=db, id_obj=user_id)
    return JSONResponse({"result": True, "user": {"id": user.id, "name": user.name,
                                                  "followers": [usr.to_dict() for usr in user.followers],
                                                  "following": [usr.to_dict() for usr in user.followed]}},
                        status_code=200)
