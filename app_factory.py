from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from typing import Optional, Tuple
import fastapi
import routers.admin_api

# TODO TODO TODO
def make_app(environment: str = "development") -> fastapi.applications.FastAPI:
    app = fastapi.FastAPI()

    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.mount("/templates", StaticFiles(directory="templates"), name="templates")

    app.include_router(routers.admin_api.make_router(db), tags=["admin-api"], prefix="/api/admin")

    templates = Jinja2Templates(directory="templates")

    # @app.post("/api/signin")
    # async def api_signin(username: str = Form(...), password: str = Form(...)):
    #     user = .authentication.get_user_by_username_and_password_or_none(db, username, password)
    #     if not user:
    #         raise HTTPException(
    #             status_code=HTTP_401_UNAUTHORIZED,
    #             detail="Incorrect username or password",
    #             headers={"WWW-Authenticate": "Bearer"},
    #         )
    #     access_token = .authentication.generate_access_token(username=user.username)
    #     return {"access_token": access_token, "token_type": "bearer"}
    # 
    # @app.post("/api/signup")
    # async def api_signup(username: str = Form(...), email: str = Form(...), password1: str = Form(...),
    #                      password2: str = Form(...), fullname: str = Form("")):
    #     preexisting_user = .authentication.get_db_user_or_none(db, username=username)
    #     if preexisting_user:
    #         raise HTTPException(
    #             status_code=HTTP_403_FORBIDDEN,
    #             detail="Username already exists",
    #         )
    #     preexisting_user = .authentication.get_db_user_or_none(db, email=email)
    #     if preexisting_user:
    #         raise HTTPException(
    #             status_code=HTTP_403_FORBIDDEN,
    #             detail="Email address already used",
    #         )
    #     salt = .authentication.generate_salt()
    #     if password1 == password2:
    #         hashed = .authentication.hash_password(salt, password2)
    #     else:
    #         raise HTTPException(
    #             status_code=HTTP_403_FORBIDDEN,
    #             detail="Passwords do not coincide",
    #         )
    #     .authentication.create_db_user(db, username=username, email=email, salt=salt, hashed=hashed, fullname=fullname)
    #     return {"detail": "User {} has been signed up.".format(username)}
    #
    # 
    # ### FRONTEND ENDPOINTS
    # 
    # @app.get("/test")
    # async def test():
    #     with db_session:
    #         db.User(username="user", email="email", salt="salt", hashed="hashed")
    #     return "done"
    # 
    # @app.get("/")
    # async def render_root(request: Request, access_token: str = Cookie(None)):
    #     current_user = .authentication.get_user_by_access_token_or_none(db=db, token=access_token)
    #     return templates.TemplateResponse("index.html", {"request": request, "current_user": current_user})
    # 
    # @app.post("/login")
    # async def login(username: str = Form(...), password: str = Form(...)):
    #     user = .authentication.get_user_by_username_and_password_or_none(db, username, password)
    #     response = RedirectResponse(url="/", status_code=303)
    #     if not user:
    #         raise HTTPException(
    #             status_code=HTTP_401_UNAUTHORIZED,
    #             detail="Incorrect username or password",
    #             headers={"WWW-Authenticate": "Bearer"},
    #         )
    #     access_token_expires = timedelta(minutes=.authentication.ACCESS_TOKEN_EXPIRE_MINUTES)
    #     access_token = .authentication.generate_access_token(
    #         username=user.username, expires_delta=access_token_expires
    #     )
    #     response.set_cookie('access_token', access_token, expires=36000)
    #     return response
    # 
    # @app.post("/logout")
    # async def logout():
    #     response = RedirectResponse(url="/", status_code=303)
    #     response.delete_cookie("access_token")
    #     return response
    # 
    # @app.post("/token")
    # async def login_for_access_token(username: str = Form(...), password: str = Form(...)):
    #     user = .authentication.get_user_by_username_and_password_or_none(db, username, password)
    #     if not user:
    #         raise HTTPException(
    #             status_code=HTTP_401_UNAUTHORIZED,
    #             detail="Incorrect username or password",
    #             headers={"WWW-Authenticate": "Bearer"},
    #         )
    #     access_token = .authentication.generate_access_token(username=user.username)
    #     return {"access_token": access_token, "token_type": "bearer"}
    # 
    # @app.post("/register")
    # async def register_for_access_token(username: str = Form(...), email: str = Form(...), password1: str = Form(...),
    #                                     password2: str = Form(...), fullname: str = Form("")):
    #     preexisting_user = .authentication.get_db_user_or_none(db, username=username)
    #     if preexisting_user:
    #         raise HTTPException(
    #             status_code=HTTP_403_FORBIDDEN,
    #             detail="Username already exists",
    #         )
    #     preexisting_user = .authentication.get_db_user_or_none(db, email=email)
    #     if preexisting_user:
    #         raise HTTPException(
    #             status_code=HTTP_403_FORBIDDEN,
    #             detail="Email address already used",
    #         )
    #     salt = helpers.generate_salt()
    #     if password1 == password2:
    #         hashed = .authentication.hash_password(salt, password2)
    #     else:
    #         raise HTTPException(
    #             status_code=HTTP_403_FORBIDDEN,
    #             detail="Passwords do not coincide",
    #         )
    #     .authentication.create_db_user(db, username=username, email=email, salt=salt, hashed=hashed, fullname=fullname)
    #     access_token = .authentication.generate_access_token(username=username)
    #     return {"access_token": access_token, "token_type": "bearer"}
    # 
    # @app.get("/login_proof/")
    # async def login_proof(current_user):
    #     return {"current_user": current_user}

    # return app, db
    return app
