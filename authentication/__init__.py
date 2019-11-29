from fastapi.param_functions import Form
from .helpers import get_salt
from .helpers import get_serial
from .helpers import hash_password
from .helpers import verify_password
import jwt
import os

from jwt import PyJWTError
from datetime import datetime
from datetime import timedelta
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from ponydb import db_session, commit
from ponydb import test_db as db
from pydantic import BaseModel
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_403_FORBIDDEN

SECRET_KEY = os.getenv('BLOOMINGMATH_SECRET_KEY', 'development_key')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

class User(BaseModel):
    username: str
    email: str = None
    full_name: str = None
    disabled: bool = None

class UserInDB(User):
    hashed: str

@db_session
def get_user(db, **kwargs):
    try:
        db_user = db.User.get(**kwargs)
        return UserInDB(**db_user.to_dict())
    except:
        return None


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM).decode("utf-8")
    print("creating access_token", encoded_jwt)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        print("get_current_user:\t", user)
        raise credentials_exception
    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

@db_session
def authenticate_user(db, username: str, password: str):
    user = db.User.get(username=username)
    if not user:
        return False
    if not verify_password(user.salt, user.hashed, password):
        return False
    return user


@db_session
def create_user(username, email, salt, hashed, fullname=""):
    newuser = db.User(
        username=username,
        email=email,
        salt=salt,
        hashed=hashed,
        fullname=fullname,
    )
    commit()
    return newuser

class OAuth2RegistrationRequestForm:
    def __init__(
            self,
            grant_type: str = Form(None, regex="password"),
            username: str = Form(...),
            password1: str = Form(...),
            password2: str = Form(...),
            email: str = Form(...),
            fullname: str = Form(""),
            scope: str = Form(""),
    ):
        self.grant_type = grant_type
        self.username = username
        self.password1 = password1
        self.password2 = password2
        self.email = email
        self.fullname= fullname
        self.scopes = scope.split()

def get_current_user_or_none(token):
    print("got token:", token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("payload:", payload)
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except PyJWTError as err:
        print("PyJWTError", err)
        return None
    user = get_user(db, username=username)
    return user

__all__ = ['get_serial', 'get_salt', 'hash_password', 'verify_password']