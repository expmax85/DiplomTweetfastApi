from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from src.database import session, cruds
from src.models import schemas


router = APIRouter()


@router.post("/tweets", response_model=schemas.Tweet)
async def create_tweet(tweet: schemas.TweetCreate, db: Session = Depends(session)):
    tweet = cruds.tweet_orm.create(db=db, obj_in=tweet)
    return JSONResponse({"result": True, "tweet_id": tweet.id}, status_code=201)


@router.post("/media")
async def add_media(media, db: Session = Depends(session)):
    return {"result": True, "media_id": 1}


@router.delete("/tweets/{tweet_id}")
def remove_tweet(tweet_id: int, db: Session = Depends(session)):
    cruds.tweet_orm.remove(db=db, id_obj=tweet_id)
    return {"result": True}


@router.post("/tweets/{tweet_id}/likes")
def create_like(tweet_id: int, db: Session = Depends(session)):
    return {"result": True}


@router.delete("/tweets/{tweet_id}/likes")
def remove_like(tweet_id: int, db: Session = Depends(session)):
    return {"result": True}


@router.get("/tweets", response_model=None)
def get_tweets(db: Session = Depends(session)):
    return {"result": True, "tweets": [
        {"id": 1, "content": "string", "attachments": [], "author":
            {"id": 1, "name": "string"},
         "likes": [],
         }
    ]}

