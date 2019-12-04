import os

if os.environ.get("SCALING_SPOON_PRODUCTION"):
    del os.environ["SCALING_SPOON_PRODUCTION"]

ROOT_URL = "http://127.0.0.1:8000"

from starlette.testclient import TestClient
from app_factory import make_app

app, db = make_app()
client = TestClient(app)

def test_online():
    assert client.get("/") is not None
