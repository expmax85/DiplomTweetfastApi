import pytest

from src.exceptions import UnAuthorizedError


@pytest.mark.asyncio
async def test_get_all_users(test_app):
    response = await test_app.get('/users', headers={"api-key": "test"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_unauthorized(test_app):
    with pytest.raises(UnAuthorizedError):
        await test_app.get('/users/me', headers={"api-key": "wrong"})


@pytest.mark.asyncio
async def test_get_me(test_app):
    response = await test_app.get('/users/me', headers={"api-key": "test"})
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert "user" in data
    assert data["user"]["name"] == "John"


@pytest.mark.asyncio
async def test_get_user_info(test_app):
    response = await test_app.get('/users', headers={"api-key": "test"})
    data = response.json()
    lu = data[1]['user']['id']
    response = await test_app.get(f'/users/{lu}', headers={"api-key": "test"})
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert "user" in data
    assert data["user"]["name"] == "Mike"


@pytest.mark.asyncio
async def test_follow(test_app):
    response = await test_app.get('/users', headers={"api-key": "test"})
    data = response.json()
    lu = data[1]['user']['id']
    response = await test_app.post(f'/users/{lu}/follow', headers={"api-key": "test"})
    assert response.status_code == 201
    assert response.json() == {"result": True}
