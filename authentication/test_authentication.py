import ponydb
import unittest
import authentication
import helpers.encryption

db = ponydb.test_db()

with ponydb.db_session:
    db.User.select().delete(bulk=True)
    db.User(
        username='user',
        email='user@example.com',
        salt='2a32b895a0f259276050f38565381b99e22a6d65db06eaf453b7df51eaf41dc5',
        hashed=helpers.encryption.hash_password('2a32b895a0f259276050f38565381b99e22a6d65db06eaf453b7df51eaf41dc5',
                                                'pass')
    )


class TestAuthentication(unittest.TestCase):
    def test_get_db_user_or_none(self):
        self.assertIsNotNone(authentication.get_db_user_or_none(db, username="user"))
        self.assertIsNotNone(authentication.get_db_user_or_none(db, email="user@example.com"))
        self.assertIsNone(authentication.get_db_user_or_none(db, email="wrong@example.com"))
        self.assertIsNone(authentication.get_db_user_or_none(db, username="wrong"))
        self.assertIsNone(authentication.get_db_user_or_none(db, wrong="wrong"))
        self.assertIsInstance(authentication.get_db_user_or_none(db, username="user"), db.User)
        self.assertEqual("user@example.com", authentication.get_db_user_or_none(db, username="user").to_dict()["email"])

    def test_create_db_user(self):
        self.assertIsNone(authentication.get_db_user_or_none(db, username="otheruser"))
        authentication.create_db_user(
            db=db,
            username="otheruser",
            email="otheruser@example.com",
            salt="2a32b895a0f259276050f38565381b99e22a6d65db06eaf453b7df51eaf41dc5",
            hashed=helpers.encryption.hash_password('2a32b895a0f259276050f38565381b99e22a6d65db06eaf453b7df51eaf41dc5',
                                                    'pass'),
            fullname="Other User"
        )
        self.assertIsNotNone(authentication.get_db_user_or_none(db, username="otheruser"))

    def test_get_user_by_username_and_password_or_none(self):
        self.assertIsNotNone(authentication.get_user_by_username_and_password_or_none(db, "user", "pass"))
        self.assertIsNone(authentication.get_user_by_username_and_password_or_none(db, "user", "notpass"))
        self.assertIsNone(authentication.get_user_by_username_and_password_or_none(db, "notuser", "pass"))

    def test_access_token_encoding_and_decoding(self):
        token = authentication.generate_access_token("user")
        self.assertIsInstance(token, str)
        self.assertIsInstance(authentication.get_user_by_access_token_or_none(db, token), db.User)


if __name__ == "__main__":
    unittest.main()
