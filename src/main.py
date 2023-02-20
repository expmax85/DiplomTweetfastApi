from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import HTMLResponse

from src.database.utils import create_users
from src.routes import tweets, users, tokens
from src.routes.tokens import oauth2_scheme

app_api = FastAPI(title='api')
app = FastAPI(title='main')


app.mount('/api', app_api, name='api')
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app_api.swagger_ui_init_oauth = oauth2_scheme
app_api.include_router(tweets.router)
app_api.include_router(users.router)
app_api.include_router(tokens.router)


@app.on_event("startup")
async def startup_event():
    await create_users()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
