import os

if os.environ.get("SCALING_SPOON_PRODUCTION"):
    # raise Exception("Do not run tests with production database")
    del os.environ["SCALING_SPOON_PRODUCTION"]

from authentication.tests import *

# from .auth_api import *
import unittest
from requests import get
from requests import post

ROOT_URL = "http://127.0.0.1:8000"


class TestApi(unittest.TestCase):
    """
    This TestCase is supposed to work with a running instance of the app.
    Before testing, start the server with
    $ uvicorn main:app --reload
    """
    from ponydb import db
    from ponydb import db_session
    import authentication

    @classmethod
    @db_session
    def setUpClass(cls):
        db.Group(short='*admin')
        db.User(username='admin', email='admin@example.com', salt='randomsalt',
                hashed=authentication.hash_password('randomsalt', 'pass'))

    def test_api_authentication(self):
        resp = post("{}/api/signup".format(ROOT_URL), data={
            "username": "reguser",
            "email": "reguser@example.com",
            "password1": "pass",
            "password2": "pass",
            "fullname": "User Registered",
        })
        self.assertEqual(resp.status_code, 200)
        resp = post("{}/api/signin".format(ROOT_URL), data={
            "username": "reguser",
            "password": "pass",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access_token", resp.json().keys())

    def test_admin_api(self):
        pass


class TestHtmlFrontend(unittest.TestCase):
    """
    This TestCase is supposed to work with a running instance of the app.
    Before testing, start the server with
    $ uvicorn main:app --reload
    """

    def setUp(self):
        assert os.environ.get("SCALING_SPOON_PRODUCTION") is None

    def test_root_page(self):
        resp = get("{}/".format(ROOT_URL))
        self.assertIn('<a class="navbar-brand" href="#">Bloomingmath</a>', resp.text)



if __name__ == "__main__":
    unittest.main()
