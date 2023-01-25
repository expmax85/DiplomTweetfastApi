from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from src.models.models import init_db, create_users
from src.routes import tweets, users


app_api = FastAPI(title='api')
app = FastAPI(title='main')

app.mount('/api', app_api, name='api')
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app_api.include_router(tweets.router)
app_api.include_router(users.router)


@app.on_event("startup")
async def startup_event():
    init_db()
    create_users()


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
