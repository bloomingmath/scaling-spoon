from popy import ModelContainer  # , db_session, Required, Optional
import helpers.encryption
from routers import stage_a
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import fastapi
from importlib import import_module
from blinker import signal
from helpers import load_flashes

# Import bases (pony-like classes) and generate database, database's models, schemas and operations
bases = import_module("bases")
mc = ModelContainer(bases, provider="sqlite", filename=":memory:", create_db=True)

# Create fastapi application with templates, static files, endpoints from routers and session middleware
app = fastapi.FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(stage_a.make_router(mc, app, templates))
app.add_middleware(SessionMiddleware, secret_key=helpers.encryption.generate_salt())

# Set up blinker signaling system
app.signals = {
    "message-flash": signal("message-flash"),
}
app.context_store = {}
signal("message-flash").connect(load_flashes)
