from .helpers import generate_salt
from .helpers import generate_serial
from .helpers import hash_password
from .helpers import verify_password

from datetime import datetime
from datetime import timedelta

from pony.orm import Database

from ponydb import db_session
from ponydb import std_db as db

from typing import Any
from typing import Optional

import jwt
import os

SECRET_KEY = os.getenv("BLOOMINGMATH_SECRET_KEY", "development_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@db_session
def get_db_user_or_none(db: Database, **kwargs: Any) -> Optional[db.User]:
    """Given a pony.orm database any kwargs, try to get the User for such arguments.
    If any exception happens it returns None."""
    try:
        db_user = db.User.get(**kwargs)
        return db_user
    except Exception as err:
        # print("In get_db_user_or_none exception:", err)
        return None


@db_session
def create_db_user(db: Database, username: str, email: str, salt: str, hashed: str, fullname: str = "") -> db.User:
    """Create a new user with given parameters and store it in db."""
    return db.User(username=username, email=email, salt=salt, hashed=hashed, fullname=fullname)


@db_session
def get_user_by_username_and_password_or_none(db: Database, username: str, password: str) -> Optional[db.User]:
    """If correct username/password are provided, fetch the user from db.
    If any exception happens it returns None."""
    try:
        db_user = db.User.get(username=username)
        if verify_password(db_user.salt, db_user.hashed, password):
            return db_user
        return None
    except Exception as err:
        return None


@db_session
def get_user_by_access_token_or_none(db: Database, token: str) -> Optional[db.User]:
    """If valid token is provided, fetch the user from db.
    If any exception happens it returns None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return None
        db_user = db.User.get(username=username)
        return db_user
    except Exception as err:
        print("In get_user_by_access_token_or_none:", err)
        return None


def generate_access_token(username: str, expires_delta: timedelta = None) -> str:
    """Generate access token for later access of user with username."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM).decode("utf-8")
    return encoded_jwt


__all__ = ["create_db_user", "generate_access_token", "get_db_user_or_none", "get_user_by_access_token_or_none",
           "get_user_by_username_and_password_or_none"]
