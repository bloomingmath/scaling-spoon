import authentication
import jwt
import os

from datetime import datetime
from datetime import timedelta
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from ponydb import db_session, commit
from ponydb import test_db as db
from pydantic import BaseModel
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_403_FORBIDDEN

SECRET_KEY = os.getenv('BLOOMINGMATH_SECRET_KEY', 'development_key')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/public", StaticFiles(directory="reactfrontend/public"), name="frontend")

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
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
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
        raise credentials_exception
    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

@db_session
def authenticate_user(db, username: str, password: str):
    user = db.User.get(username=username)
    if not user:
        return False
    if not authentication.verify_password(user.salt, user.hashed, password):
        return False
    return user

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("reactfrontend/index.html", "r") as f:
        return f.read()

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

from fastapi.param_functions import Form

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

@app.post("/register", response_model=Token)
async def register_for_access_token(form_data: OAuth2RegistrationRequestForm = Depends()):
    print("At least here:")
    prexisting_user = get_user(db, username=form_data.username)
    if prexisting_user:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Username already exists",
        )
    prexisting_user = get_user(db, email=form_data.email)
    if prexisting_user:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Email address already used",
        )
    salt = authentication.get_salt()
    if form_data.password1==form_data.password2:
        hashed = authentication.hash_password(salt, form_data.password2)
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Passwords do not coincide",
        )
    new_user = create_user(username=form_data.username, email=form_data.email, salt=salt, hashed=hashed, fullname=form_data.fullname)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/login_proof/")
async def login_proof(current_user: User = Depends(get_current_user)):
    return {"current_user": current_user}