import os
import shutil

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

from src.config import settings
from src.database import session, cruds
from src.database.cruds import create_image
from src.models import schemas, User
from src.models.utils import to_json
from src.routes.users import get_user

router = APIRouter()


@router.post("/tweets", response_model=schemas.TweetSuccess, status_code=status.HTTP_201_CREATED)
async def create_tweet(tweet: schemas.TweetCreate, db: Session = Depends(session),
                       user: User = Depends(get_user)):
    tweet = cruds.tweets_orm.create(db=db, obj_in=tweet, user_id=user.id)
    # tweet.attachments.append(image)
    # db.commit()
    # db.refresh(user)
    print(tweet)
    return {"result": True, "tweet_id": tweet.id}


@router.post("/medias", response_model=None)
async def add_media(media: UploadFile = File(...), db: Session = Depends(session)):
    path = os.path.join(settings.UPLOADS_DIR, media.filename)
    with open(path, "wb") as wf:
        shutil.copyfileobj(media.file, wf)
        media.file.close()
        path = f'/static/images/{media.filename}'
        image = create_image(db=db, file=str(path), tweet_id=1)
    return {"result": True, "media_id": image.id}


@router.delete("/tweets/{tweet_id}", response_model=schemas.Success)
def remove_tweet(tweet_id: int, db: Session = Depends(session), user: User = Depends(get_user)):
    tweet = cruds.tweets_orm.get(db=db, id_obj=tweet_id)
    if tweet.is_author(user):
        cruds.tweets_orm.remove(db=db, id_obj=tweet_id)
        return {"result": True}
    raise HTTPException(detail='error', status_code=status.HTTP_405_METHOD_NOT_ALLOWED)



@router.post("/tweets/{tweet_id}/likes", response_model=schemas.Success)
def create_like(tweet_id: int, db: Session = Depends(session), user: User = Depends(get_user)):
    cruds.tweets_orm.create_like(db=db, tweet_id=tweet_id, user_id=user.id)
    return {"result": True}


@router.delete("/tweets/{tweet_id}/likes", response_model=schemas.Success)
def remove_like(tweet_id: int, db: Session = Depends(session), user: User = Depends(get_user)):
    cruds.tweets_orm.remove_like(db=db, tweet_id=tweet_id, user_id=user.id)
    return {"result": True}


@router.get("/tweets")
def get_tweets(db: Session = Depends(session)):
    tweets = cruds.tweets_orm.get_all(db)
    tweets = schemas.Tweets(result=True, tweets=tweets)
    tweets = to_json(tweets)
    print(tweets)
    return tweets
