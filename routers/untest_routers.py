ROOT_URL = "http://127.0.0.1:8000"

from starlette.testclient import TestClient
import fastapi
from main import *
from popy import *

models = __import__("models")
db = generate_database(models, provider="sqlite", filename=":memory:", create_db=True)
app = fastapi.FastAPI()
client = TestClient(app, base_url="http://127.0.0.1:8000")


def test_api_admin():
    from ponydb.test_ponydb import populate_test_db
    populate_test_db(db)
    print(client.get("/api/admin/users").json())
    assert len(client.get("/api/admin/users").json()) == 43
