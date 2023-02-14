from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from src.database.cruds import create_image, TweetAction

from src.database.cruds import get_tweet_service
from src.models import schemas, User
from src.models.utils import to_json
from src.routes.users import get_user

router = APIRouter()


@router.post("/tweets", response_model=schemas.TweetSuccess, status_code=status.HTTP_201_CREATED)
async def create_tweet(tweet: schemas.TweetCreate, tweet_service: TweetAction = Depends(get_tweet_service),
                       user: User = Depends(get_user)):
    tweet = tweet_service.create(obj_in=tweet, user_id=user.id)
    # tweet.attachments.append(image)
    # db.commit()
    # db.refresh(user)
    print(tweet)
    return {"result": True, "tweet_id": tweet.id}


# @router.post("/medias", response_model=None)
# async def add_media(media: UploadFile = File(...)):
#     path = os.path.join(settings.UPLOADS_DIR, media.filename)
#     with open(path, "wb") as wf:
#         shutil.copyfileobj(media.file, wf)
#         media.file.close()
#         path = f'/static/images/{media.filename}'
#         image = create_image(session=db, file=str(path))
#     return {"result": True, "media_id": image.id}


@router.delete("/tweets/{tweet_id}", response_model=schemas.Success)
def remove_tweet(tweet_id: int, tweet_service: TweetAction = Depends(get_tweet_service), user: User = Depends(get_user)):
    tweet = tweet_service.get(id_obj=tweet_id)
    if tweet.is_author(user):
        tweet_service.remove(id_obj=tweet_id)
        return {"result": True}
    raise HTTPException(detail='error', status_code=status.HTTP_405_METHOD_NOT_ALLOWED)



@router.post("/tweets/{tweet_id}/likes", response_model=schemas.Success)
def create_like(tweet_id: int, tweet_service: TweetAction = Depends(get_tweet_service), user: User = Depends(get_user)):
    tweet_service.create_like(tweet_id=tweet_id, user_id=user.id)
    return {"result": True}


@router.delete("/tweets/{tweet_id}/likes", response_model=schemas.Success)
def remove_like(tweet_id: int, tweet_service: TweetAction = Depends(get_tweet_service), user: User = Depends(get_user)):
    tweet_service.remove_like(tweet_id=tweet_id, user_id=user.id)
    return {"result": True}


@router.get("/tweets")
def get_tweets(tweet_service: TweetAction = Depends(get_tweet_service)):
    tweets = tweet_service.get_all()
    tweets = schemas.Tweets(result=True, tweets=tweets)
    tweets = to_json(tweets)
    print(tweets)
    return tweets
