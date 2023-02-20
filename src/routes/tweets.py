from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from starlette import status

from src.database import get_tweet_service, TweetAction
from src.database.cruds import MediaAction, get_media_service
from src.models import schemas, User
from src.models.utils import to_json
from src.routes.tokens import get_current_active_user

router = APIRouter()


@router.post("/tweets", response_model=schemas.TweetSuccess, status_code=status.HTTP_201_CREATED)
async def create_tweet(tweet: schemas.TweetCreate,
                       tweet_service: TweetAction = Depends(get_tweet_service),
                       user: User = Depends(get_current_active_user),
                       media_service: MediaAction = Depends(get_media_service)):
    tweet = await tweet_service.create(obj_in=tweet, user_id=user.id)
    await media_service.update(tweet)
    return {"result": True, "tweet_id": tweet.id}


@router.post("/medias")
async def add_media(file: UploadFile = File(...), media_service: MediaAction = Depends(get_media_service)):
    image = await media_service.create(file=file)
    return {"result": True, "media_id": image.id}


@router.delete("/tweets/{tweet_id}", response_model=schemas.Success)
async def remove_tweet(tweet_id: int, tweet_service: TweetAction = Depends(get_tweet_service),
                       user: User = Depends(get_current_active_user),
                       media_service: MediaAction = Depends(get_media_service)):
    tweet = await tweet_service.get(id_obj=tweet_id)
    if tweet.is_author(user):
        await media_service.remove(tweet=tweet)
        await tweet_service.remove(id_obj=tweet_id)
        return {"result": True}
    raise HTTPException(detail='error', status_code=status.HTTP_405_METHOD_NOT_ALLOWED)


@router.post("/tweets/{tweet_id}/likes", response_model=schemas.Success)
async def create_like(tweet_id: int,
                      tweet_service: TweetAction = Depends(get_tweet_service),
                      user: User = Depends(get_current_active_user)):
    await tweet_service.create_like(tweet_id=tweet_id, user_id=user.id)
    return {"result": True}


@router.delete("/tweets/{tweet_id}/likes", response_model=schemas.Success)
async def remove_like(tweet_id: int,
                      tweet_service: TweetAction = Depends(get_tweet_service),
                      user: User = Depends(get_current_active_user)):
    await tweet_service.remove_like(tweet_id=tweet_id, user_id=user.id)
    return {"result": True}


@router.get("/tweets")
async def get_tweets(tweet_service: TweetAction = Depends(get_tweet_service)):
    tweets = await tweet_service.get_all()
    tweets = schemas.TweetsSerialize(tweets=tweets)
    tweets = to_json(tweets)
    return tweets
