from importlib import import_module
from popy import generate_popy, db_session
from routers import frontend, tmp
from starlette.templating import Jinja2Templates
from starlette.testclient import TestClient
from starlette.staticfiles import StaticFiles

import fastapi

database, schemas, operations = generate_popy(import_module("models"), provider="sqlite", filename=":memory:",
                                              create_db=True)

testapp = fastapi.FastAPI()

templates = Jinja2Templates(directory="templates")

testapp.mount("/static", StaticFiles(directory="static"), name="static")

testapp.include_router(frontend.make_router(database, schemas, operations, testapp, templates, db_session))
testapp.include_router(tmp.make_router(database, schemas, operations, testapp, templates, db_session), prefix="/tmp")

client = TestClient(testapp)


def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "Benvenut@ Eternauta" in response.text


def test_tmp_upload():
    files = {"file": open("README.md", "rb")}
    response = client.post("/tmp/upload", files=files)
    assert response.status_code == 422
    response = client.post("/tmp/upload", files=files, data={"short": "project's readme", "filetype": "md"})
    assert response.status_code == 200
    assert "new_content" in response.json()
    new_content = response.json()["new_content"]
    assert "serial" in new_content
    serial = new_content["serial"]
    filetype = new_content["filetype"]
    import os
    os.remove(f"static/contents/{serial}.{filetype}")


if __name__ == "__main__":
    test_homepage()
