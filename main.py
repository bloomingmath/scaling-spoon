from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

from extensions.signals import signals_engine
from extensions.rendering import render_engine
from extensions.mongo import mongo_engine
from extensions.security import generate_salt
from routers import users, main, groups, contents
from dotenv import load_dotenv
from os import getenv

load_dotenv()
FASTAPI_ENVIRONMENT = getenv("FASTAPI_ENVIRONMENT", "development")
MONGODB_URI = getenv("MONGODB_URI", "mongodb://localhost:27017")

# Create fastapi application with rendering engine, motor mongodb connection, static files and signaling system
app = FastAPI(title="Scaling spoon")


app.mount("/static", StaticFiles(directory="static"), name="static")
# mongo_engine.init_app(app)
mongo_engine.init_app(app, uri=MONGODB_URI, env=FASTAPI_ENVIRONMENT)
render_engine.init_app(app)
signals_engine.init_app(app)


# Add middlewares
@app.middleware("http")
async def next_url_redirect(request: Request, call_next):
    """Check if 'next' query parameter is present in the request. If so, inject it as next url in an eventual Http303
    response. """
    try:
        url = request.query_params["next"]
        assert isinstance(url, str)
        assert len(url) > 0
        assert url[0] == "/"
    except (AttributeError, KeyError, AssertionError):
        url = None

    response = await call_next(request)
    if url is not None and response.status_code == 303:
        response.headers["location"] = url
    return response

app.add_middleware(SessionMiddleware, secret_key=generate_salt())

# Include routers
app.include_router(main.router)
app.include_router(users.router, prefix="/users")
app.include_router(groups.router, prefix="/groups")
app.include_router(contents.router, prefix="/contents")


if __name__ == "__main__":
    from uvicorn import run

    run(app, port=8080)
