import pytest

from src.exceptions import NotAllowedError, TweetNotExist


@pytest.mark.asyncio
async def test_create_tweet(test_app):
    response = await test_app.post(
        "/tweets",
        json={"tweet_data": "test tweet message", "tweet_media_ids": []},
        headers={"api-key": "test"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["result"] is True
    assert "tweet_id" in data


@pytest.mark.asyncio
async def test_get_tweets(test_app):
    response = await test_app.get("/tweets", headers={"api-key": "test"})
    assert response.status_code == 200
    data = response.json()
    assert "tweets" in data
    assert len(data["tweets"]) == 2


@pytest.mark.asyncio
async def test_delete_own_tweet(test_app):
    last_tweet = await test_app.get("/tweets", headers={"api-key": "test"})
    lti = last_tweet.json()["tweets"][0]["id"]
    response = await test_app.delete(f"/tweets/{lti}", headers={"api-key": "test"})
    assert response.status_code == 202
    assert response.json() == {"result": True}


@pytest.mark.asyncio
async def test_delete_not_author_tweet(test_app):
    last_tweet = await test_app.get("/tweets", headers={"api-key": "test"})
    data = last_tweet.json()["tweets"]
    with pytest.raises(NotAllowedError):
        await test_app.delete(f'/tweets/{data[1]["id"]}', headers={"api-key": "test"})


@pytest.mark.asyncio
async def test_create_like(test_app):
    last_tweet = await test_app.get("/tweets", headers={"api-key": "test"})
    data = last_tweet.json()["tweets"]
    lti = data[0]["id"]
    response = await test_app.post(f"/tweets/{lti}/likes", headers={"api-key": "test"})
    assert response.status_code == 200
    assert response.json() == {"result": True}


@pytest.mark.asyncio
async def test_remove_not_self_like(test_app):
    last_tweet = await test_app.get("/tweets", headers={"api-key": "test"})
    data = last_tweet.json()["tweets"]
    lti = data[1]["id"]
    with pytest.raises(TweetNotExist):
        await test_app.delete(f"/tweets/{lti}/likes", headers={"api-key": "test"})
