from popy import Required, Optional, ModelContainer, db_session
import helpers.encryption
from routers import frontend, stage01
from starlette.templating import Jinja2Templates
from starlette.testclient import TestClient
from starlette.staticfiles import StaticFiles
import fastapi


def fake_module(name: str):
    from types import ModuleType

    m = ModuleType(name)

    class User:
        username = Required(str, unique=True)
        email = Required(str, unique=True)
        salt = Required(str)
        hashed = Required(str)
        fullname = Optional(str)

        def create_preparation(self, username: str, email: str, password: str, fullname: str = None):
            salt = helpers.encryption.generate_salt()
            hashed = helpers.encryption.hash_password(salt, password)
            create_info = {"username": username, "email": email, "salt": salt, "hashed": hashed}
            if fullname is not None:
                create_info["fullname"] = fullname
            return create_info

        def get_preparation(self, id: int = None, username: str = None, email: str = None):
            get_info = {}
            if id is not None:
                get_info["id"] = id
            if username is not None:
                get_info["username"] = username
            if email is not None:
                get_info["email"] = email
            return get_info

        def select_preparation(self):
            select_info = {}
            return select_info

        def update_preparation(self, password: str = None, fullname: str = None):
            update_info = {}
            if password is not None:
                salt = self.salt
                hashed = helpers.encryption.hash_password(salt, password)
                update_info["hashed"] = hashed
            if fullname is not None:
                update_info["fullname"] = fullname
            return update_info

    User.__module__ = name
    m.User = User
    return m


bases = fake_module("bases")

mc = ModelContainer(bases, provider="sqlite", filename=":memory:", create_db=True)

app = fastapi.FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(stage01.make_router(mc, app, templates))

client = TestClient(app)

def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "Benvenut@ Eternauta" in response.text

