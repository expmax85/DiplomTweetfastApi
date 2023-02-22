from fastapi import APIRouter, Depends, UploadFile, File
from starlette import status

from src.services import get_tweet_service, TweetService
from src.models import schemas, User
from src.exceptions import schemas as exc_schemes, get_response_scheme
from src.routes.tokens import get_current_active_user

router = APIRouter(tags=['Tweets'], responses={401: get_response_scheme(model=exc_schemes.Unauthorized)})


@router.post("/tweets", response_model=schemas.TweetSuccess, status_code=status.HTTP_201_CREATED,
             responses={409: get_response_scheme(model=exc_schemes.CreateTweetError)})
async def create_tweet(new_tweet: schemas.TweetCreate,
                       tweet_service: TweetService = Depends(get_tweet_service),
                       user: User = Depends(get_current_active_user)):
    """ Create new tweet.

     - **tweet** - data creating tweet in json format with keys 'tweet_data' - tweet test message,
     'tweet_media_ids; - not required, media_ids list for tweet images. """
    return await tweet_service.create(data=new_tweet, user_id=user.id)


@router.post("/medias", response_model=schemas.MediaSuccess, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_current_active_user)],
             responses={400: get_response_scheme(model=exc_schemes.SizeImgError)})
async def add_media(file: UploadFile = File(...), tweet_service: TweetService = Depends(get_tweet_service)):
    """ Uploading tweet images.

     - **file** - uploading image file"""
    return await tweet_service.add_media(file=file)


@router.delete("/tweets/{tweet_id}", response_model=schemas.Success, status_code=status.HTTP_201_CREATED,
               responses={404: get_response_scheme(model=exc_schemes.TweetNotExist),
                          403: get_response_scheme(model=exc_schemes.NotAllowedError)})
async def remove_tweet(tweet_id: int,
                       tweet_service: TweetService = Depends(get_tweet_service),
                       user: User = Depends(get_current_active_user)):
    """ Remove tweet.

     - **tweet_id** - id by removing tweet"""
    return await tweet_service.remove(tweet_id=tweet_id, user=user)


@router.post("/tweets/{tweet_id}/likes", response_model=schemas.Success,
             responses={404: get_response_scheme(model=exc_schemes.TweetNotExist)})
async def create_like(tweet_id: int,
                      tweet_service: TweetService = Depends(get_tweet_service),
                      user: User = Depends(get_current_active_user)):
    """ Like tweet.

     - **tweet_id** - id by liking tweet"""
    return await tweet_service.create_like(tweet_id=tweet_id, user_id=user.id)


@router.delete("/tweets/{tweet_id}/likes", response_model=schemas.Success,
               responses={404: get_response_scheme(model=exc_schemes.TweetNotExist)})
async def remove_like(tweet_id: int,
                      tweet_service: TweetService = Depends(get_tweet_service),
                      user: User = Depends(get_current_active_user)):
    """ Dislike tweet.

     - **tweet_id** - id by disliking tweet"""
    return await tweet_service.remove_like(tweet_id=tweet_id, user_id=user.id)


public_router = APIRouter(tags=['Public'])


@public_router.get("/tweets", response_model=schemas.TweetsResponse)
async def get_tweets(skip: int = 0, limit: int = 100,
                     tweet_service: TweetService = Depends(get_tweet_service)):
    """ Get all tweets. Authenticate is not required """
    return await tweet_service.get_all(skip=skip, limit=limit)
