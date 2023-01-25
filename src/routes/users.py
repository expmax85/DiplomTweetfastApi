from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from src.database import session, cruds
from src.models import schemas
from src.models import User
from src.models.models import Token

router = APIRouter()


@router.post("/users/<id>/follow")
async def add_follow(db: Session = Depends(session)):
    return {"result": True}


@router.delete("/users/<id>/follow")
async def remove_follow(db: Session = Depends(session)):
    return {"result": True}


@router.get("/users/me")
async def get_self_info(api_key: str = Header(), db: Session = Depends(session)):
    user = db.query(User).join(Token, Token.user_id == User.id).filter(Token.api_key == api_key).first()
    if not user:
        return JSONResponse({"result": False, "error_type": "Unauthorized", "error_message": "User has no registered"},
                            status_code=200)
    return JSONResponse({"result": True, "user": {"id": user.id, "name": user.name, "followers": []}}, status_code=200)


@router.get("/users/{user_id}")
async def get_user_info(user_id: int, db: Session = Depends(session)):
    user = db.query(User).filter(User.id == user_id).first()
    return JSONResponse({"result": True, "user": {"id": user.id, "name": user.name, "followers": []}},
                        status_code=200)
