import sentry_sdk

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.config import settings
from src.exceptions import BaseCustomExc, logger
from src.routes import tokens, tweets, users


sentry_sdk.init(
    dsn=settings.App.SENTRY_DSN,
    traces_sample_rate=1.0,
)

app_api = FastAPI(debug=settings.App.DEBUG,
                  title=settings.App.TITLE,
                  description=settings.App.DESCRIPTION,
                  version=settings.App.VERSION)

app_api.swagger_ui_init_oauth = tokens.oauth2_scheme
app_api.include_router(tweets.router)
app_api.include_router(users.router)
app_api.include_router(tokens.router)
app_api.include_router(tweets.public_router)


@app_api.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, exc: Exception):
    if not isinstance(exc, BaseCustomExc):
        logger.error(''.join([str(request.url), ' - ', str(request.method)]))
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
