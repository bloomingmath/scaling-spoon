import authentication as auth
import jwt
import os

from datetime import datetime
from datetime import timedelta
from fastapi import Cookie
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from ponydb import db_session, commit
from ponydb import test_db as db
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_403_FORBIDDEN
from starlette.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/public", StaticFiles(directory="reactfrontend/public"), name="frontend")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def render_root(request: Request, access_token: str = Cookie(None)):
    current_user = auth.get_current_user_or_none(access_token)
    print("current user:", current_user)
    return templates.TemplateResponse("index.html", {"request": request, "current_user": current_user})

@app.post("/login")
async def login(form_data: auth.OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    response = RedirectResponse(url="/", status_code=303)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response.set_cookie('access_token', access_token, expires=36000)
    return response

@app.post("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response


@app.post("/token", response_model=auth.Token)
async def login_for_access_token(form_data: auth.OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=auth.Token)
async def register_for_access_token(form_data: auth.OAuth2RegistrationRequestForm = Depends()):
    print("At least here:")
    prexisting_user = auth.get_user(db, username=form_data.username)
    if prexisting_user:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Username already exists",
        )
    prexisting_user = auth.get_user(db, email=form_data.email)
    if prexisting_user:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Email address already used",
        )
    salt = auth.get_salt()
    if form_data.password1==form_data.password2:
        hashed = auth.hash_password(salt, form_data.password2)
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Passwords do not coincide",
        )
    new_user = auth.create_user(username=form_data.username, email=form_data.email, salt=salt, hashed=hashed, fullname=form_data.fullname)
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": new_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/login_proof/")
async def login_proof(current_user: auth.User = Depends(auth.get_current_user)):
    return {"current_user": current_user}