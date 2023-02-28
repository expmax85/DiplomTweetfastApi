import logging

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.exceptions import BaseCustomExc
from src.routes import tokens, tweets, users

app_api = FastAPI(title="api")

app_api.swagger_ui_init_oauth = tokens.oauth2_scheme
app_api.include_router(tweets.router)
app_api.include_router(users.router)
app_api.include_router(tokens.router)
app_api.include_router(tweets.public_router)


logger = logging.getLogger('unknown_errors')
handler = logging.FileHandler(filename='unexpected_error.log', mode='a')
handler.setLevel(logging.ERROR)
logger.addHandler(handler)


@app_api.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, exc: Exception):
    if not isinstance(exc, BaseCustomExc):
        logger.exception(exc)
        return JSONResponse(
            status_code=404,
            content={
                "result": False,
                "error_type": "UnknownError",
                "error_massage": "Unexpected error",
            },
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "result": exc.result,
            "error_type": exc.error_type,
            "error_massage": exc.error_message,
        },
    )
