from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from src.database import session, cruds
from src.models import schemas, User
from src.routes.users import get_user

router = APIRouter()


@router.post("/tweets", response_model=schemas.TweetSuccess)
async def create_tweet(tweet: schemas.TweetCreate, db: Session = Depends(session),
                       user: User = Depends(get_user)):
    tweet = cruds.tweets_orm.create(db=db, obj_in=tweet, user_id=user.id)
    return JSONResponse({"result": True, "tweet_id": tweet.id}, status_code=201)


@router.delete("/tweets/{tweet_id}", response_model=schemas.Success)
def remove_tweet(tweet_id: int, db: Session = Depends(session), user: User = Depends(get_user)):
    tweet = cruds.tweets_orm.get(db=db, id_obj=tweet_id)
    if tweet.is_author(user):
        cruds.tweets_orm.remove(db=db, id_obj=tweet_id)
    return {"result": True}


@router.post("/tweets/{tweet_id}/likes", response_model=schemas.Success)
def create_like(tweet_id: int, db: Session = Depends(session), user: User = Depends(get_user)):
    cruds.tweets_orm.create_like(db=db, tweet_id=tweet_id, user_id=user.id)
    return {"result": True}


@router.delete("/tweets/{tweet_id}/likes", response_model=schemas.Success)
def remove_like(tweet_id: int, db: Session = Depends(session), user: User = Depends(get_user)):
    cruds.tweets_orm.remove_like(db=db, tweet_id=tweet_id, user_id=user.id)
    return {"result": True}


@router.get("/tweets", response_model=schemas.Tweets)
def get_tweets(db: Session = Depends(session)):
    tweets = cruds.tweets_orm.get_all(db=db)
    print(schemas.Tweets(result=True, tweets=tweets))
    return {"result": True, "tweets": tweets}


@router.post("/media")
async def add_media(media, db: Session = Depends(session)):
    return {"result": True, "media_id": 1}

