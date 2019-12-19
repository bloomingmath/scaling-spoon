from popy import Required, Optional, ModelContainer, db_session
import helpers.encryption
from routers import stage_a
from starlette.templating import Jinja2Templates
from starlette.testclient import TestClient
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import fastapi
from helpers.middlewarehacks import BaseHTTPMiddleware
from importlib import import_module



bases = import_module("bases")

mc = ModelContainer(bases, provider="sqlite", filename=":memory:", create_db=True)

app = fastapi.FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(stage_a.make_router(mc, app, templates))
app.add_middleware(SessionMiddleware, secret_key=helpers.encryption.generate_salt())

import time
from starlette.requests import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    next_url = request.query_params.get("next", None)
    response = await call_next(request)
    if next_url:
        # response.headers['X-Custom'] = next_url
        print("Next_url", next_url)
    return response

# app.add_middleware(BaseHTTPMiddleware, dispatch=add_process_time_header)

client = TestClient(app)

def test_nextmiddleware():
    client.get("/?next=/signup")

def test_app_is_online():
    response = client.get("/")
    assert response.status_code == 200

