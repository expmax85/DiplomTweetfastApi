import asyncio

import pytest

from src.exceptions import NotAllowedError
from src.database import SQLSession, TweetAction
from src.tests import tweet_orm


@pytest.mark.asyncio
async def test_create_tweet(test_app):
    response = await test_app.post('/tweets',
                                   json={"tweet_data": 'test tweet message', "tweet_media_ids": []},
                                   headers={"api-key": "test"}
                                   )
    assert response.status_code == 201
    data = response.json()
    assert data["result"] is True
    assert "tweet_id" in data


@pytest.mark.asyncio
async def test_get_tweets(test_app):
    response = await test_app.get('/tweets', headers={"api-key": "test"})
    assert response.status_code == 200
    data = response.json()
    assert "tweets" in data
    assert len(data["tweets"]) == 3


@pytest.mark.asyncio
async def test_delete_tweet(test_app):
    last_tweet = await test_app.get('/tweets', headers={"api-key": "test"})
    lti = last_tweet.json()['tweets'][1]['id']
    print(lti)
    response = await test_app.delete(f'/tweets/{lti}', headers={'api-key': 'test'})
    assert response.status_code == 202
    # lti = last_tweet.json()['tweets'][1]['id']
    # with pytest.raises(NotAllowedError):
    #     await test_app.delete(f'/tweets/{lti}', headers={'api-key': 'test'})



# @pytest.mark.asyncio
# async def test_create_like(test_app):
#     tweet_orm = TweetAction(db=SQLSession())
#     tweets = await tweet_orm.get_all()
#     lti = tweets[0].id
#     response = await test_app.post(f'/tweets/{lti}/likes', headers={'api-key': 'test'})
#     assert response.status_code == 200
#
#
# @pytest.mark.asyncio
# async def test_remove_like(test_app):
#     tweet_orm = TweetAction(db=SQLSession())
#     tweets = await tweet_orm.get_all()
#     lti = tweets[1].id
#     response = await test_app.delete(f'/tweets/{lti}/likes', headers={'api-key': 'test'})
#     assert response.status_code == 200
