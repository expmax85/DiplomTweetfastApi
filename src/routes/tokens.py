from datetime import datetime, timedelta
from typing import Union

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from starlette.requests import Request

from src.database import UserAction, get_db
from src.models import User, schemas
from src.config import settings
from src.models.utils import verify_password


class CustomAuth2(OAuth2PasswordBearer):

    async def __call__(self, request: Request) -> Union[str, tuple, None]:
        api_key = request.headers.get('api-key')
        scheme = 'api-key'
        if api_key:
            return api_key, scheme
        return await super(CustomAuth2, self).__call__(request)


oauth2_scheme = CustomAuth2(tokenUrl="token")


async def authenticate_user(username: str, password: str):
    user = await get_user(username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_user(username: str):
    user_service = UserAction(db=get_db())
    return await user_service.get_by_name(name=username)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.App.SECRET_KEY, algorithm=settings.App.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user_service = UserAction(db=get_db())
    if 'api-key' in token:
        return await user_service.get_user_by_api_key(api_key=token[0])

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.App.SECRET_KEY, algorithms=[settings.App.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.inactive:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


router = APIRouter()


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.App.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
