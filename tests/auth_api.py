import authentication
import json
from pony.orm import commit
import requests
import shutil
import unittest

from ponydb import db_session
from ponydb import db

ROOT_URL = "http://127.0.0.1:8000"

class TestAuthApi(unittest.TestCase):
    @db_session
    def setUp(self):
        db.User.select().delete(bulk=True)
        db.User(
            username='olduser',
            email='olduser@example.com',
            salt='randomsalt',
            hashed=authentication.hash_password('randomsalt', 'pass')
        )

    def test_good_registration(self):
        form_data = {
            "username":"newuser",
            "email": "newuser@example.com",
            "password1": "pass",
            "password2": "pass",
            "fullname": "New User",
        }
        resp=requests.post("{}/register".format(ROOT_URL),
                           data=form_data)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access_token", resp.json().keys())

    def test_bad_registration1(self):
        form_data = {
            "username":"olduser",
            "email": "anything@example.com",
            "password1": "pass",
            "password2": "pass",
            "fullname": "",
        }
        resp=requests.post("{}/register".format(ROOT_URL),
                           data=form_data)
        self.assertEqual(resp.status_code, 403)
        self.assertNotIn("access_token", resp.json().keys())
        self.assertIn("detail", resp.json().keys())
        self.assertEqual("Username already exists", resp.json()["detail"])

    def test_bad_registration2(self):
        form_data = {
            "username":"newuser",
            "email": "olduser@example.com",
            "password1": "pass",
            "password2": "pass",
            "fullname": "",
        }
        resp=requests.post("{}/register".format(ROOT_URL),
                           data=form_data)
        self.assertEqual(resp.status_code, 403)
        self.assertNotIn("access_token", resp.json().keys())
        self.assertIn("detail", resp.json().keys())
        self.assertEqual("Email address already used", resp.json()["detail"])

    def test_bad_registration3(self):
        form_data = {
            "username":"newuser",
            "email": "newuser@example.com",
            "password1": "pass",
            "password2": "passs",
            "fullname": "",
        }
        resp=requests.post("{}/register".format(ROOT_URL),
                           data=form_data)
        self.assertEqual(resp.status_code, 403)
        self.assertNotIn("access_token", resp.json().keys())
        self.assertIn("detail", resp.json().keys())
        self.assertEqual("Passwords do not coincide", resp.json()["detail"])

    def test_token(self):
        form_data = {
            "username": "olduser",
            "password": "pass",
        }
        resp=requests.post("{}/token".format(ROOT_URL),
                           data=form_data)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access_token", resp.json().keys())
