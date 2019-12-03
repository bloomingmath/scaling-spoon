# from authentication.test_authentication import *
from requests import get
from requests import post
import os
import unittest

if os.environ.get("SCALING_SPOON_PRODUCTION"):
    del os.environ["SCALING_SPOON_PRODUCTION"]

ROOT_URL = "http://127.0.0.1:8000"

from starlette.testclient import TestClient
from main import app
from ponydb import test_db
from ponydb import db_session
import authentication

db = test_db()
client = TestClient(app)


class TestApi(unittest.TestCase):
    """
    This TestCase is supposed to work with a running instance of the app.
    Before testing, start the server with
    $ uvicorn main:app --reload
    """
    #
    # @classmethod
    # @db_session
    # def setUpClass(cls):
    #     try:
    #         db.Group(short='*admin')
    #         db.User(username='admin', email='admin@example.com', salt='randomsalt',
    #                 hashed=authentication.hash_password('randomsalt', 'pass'))
    #     except:
    #         print("psss...")

    def test_api_authentication(self):
        resp = client.post("{}/api/signup".format(ROOT_URL), data={
            "username": "reguser",
            "email": "reguser@example.com",
            "password1": "pass",
            "password2": "pass",
            "fullname": "User Registered",
        })
        self.assertEqual(resp.status_code, 200)
        resp = client.post("{}/api/signin".format(ROOT_URL), data={
            "username": "reguser",
            "password": "pass",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access_token", resp.json().keys())


class TestHtmlFrontend(unittest.TestCase):
    def test_root_page(self):
        resp = client.get("{}/".format(ROOT_URL))
        self.assertIn('<a class="navbar-brand" href="#">Bloomingmath</a>', resp.text)


if __name__ == "__main__":
    unittest.main()
