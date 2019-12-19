from popy import Required, Optional, ModelContainer, db_session
import helpers.encryption
from routers import stage_a
from starlette.templating import Jinja2Templates
from starlette.testclient import TestClient
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import fastapi
from importlib import import_module



bases = import_module("bases")

mc = ModelContainer(bases, provider="sqlite", filename=":memory:", create_db=True)

app = fastapi.FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(stage_a.make_router(mc, app, templates))

app.add_middleware(SessionMiddleware, secret_key=helpers.encryption.generate_salt())
