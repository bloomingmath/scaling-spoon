from popy import ModelContainer  # , db_session, Required, Optional
import helpers.encryption
from routers import stage_a
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
from importlib import import_module
from blinker import signal
from helpers import load_flashes
from starlette.requests import Request

# Import bases (pony-like classes) and generate database, database's models, schemas and operations
bases = import_module("bases")
mc = ModelContainer(bases, provider="sqlite", filename=":memory:", create_db=True)

# Create fastapi application with templates, static files, endpoints from routers and session middleware
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(stage_a.make_router(mc, app, templates))

# Adding middlewares
app.add_middleware(SessionMiddleware, secret_key=helpers.encryption.generate_salt())

@app.middleware("http")
async def next_url_redirect(request: Request, call_next):
    try:
        url = request.query_params["next"]
        assert isinstance(url, str)
        assert len(url) > 0
        assert url[0] == "/"
    except (AttributeError, KeyError, AssertionError):
        url = None

    response = await call_next(request)
    if url is not None and response.status_code == 303:
        response.headers["location"] = url
    return response

# Set up blinker signaling system
app.signals = {
    "message-flash": signal("message-flash"),
}
app.context_store = {}
signal("message-flash").connect(load_flashes)
