from importlib import import_module
from popy import generate_popy, db_session
from routers import frontend
from starlette.templating import Jinja2Templates
from starlette.testclient import TestClient
from starlette.staticfiles import StaticFiles

import fastapi

database, schemas, operations = generate_popy(import_module("models"), provider="sqlite", filename=":memory:", create_db=True)

testapp = fastapi.FastAPI()

templates = Jinja2Templates(directory="templates")

testapp.mount("/static", StaticFiles(directory="static"), name="static")

testapp.include_router(frontend.make_router(database, schemas, operations, testapp, templates))

client = TestClient(testapp)

def test_homepage():
    response = client.get("/")
    assert response.status_code == 200