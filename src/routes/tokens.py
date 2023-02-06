from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, HTTPException, APIRouter
from starlette.status import HTTP_403_FORBIDDEN


api_key_header = APIKeyHeader(name="access_token")

API_KEY = 'test'


async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )


# @router.get("/secure")
# async def info(api_key: APIKey = Depends(get_api_key)):
#     return {
#         "default variable": api_key
#     }
#
#
# # Open Route
# @router.get("/open")
# async def info():
#     return {
#         "default variable": "Open Route"
#     }