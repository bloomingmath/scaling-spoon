ROOT_URL = "http://127.0.0.1:8000"

from starlette.testclient import TestClient
import fastapi
import ponydb

db = ponydb.test_db()
app = fastapi.FastAPI()
client = TestClient(app)

def test_online():
    assert client.get("/") is not None
