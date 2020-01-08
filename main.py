from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

from extensions import mongo_engine, render_engine, signals_engine
from helpers import generate_salt
from routers import users, main, groups

# Create fastapi application with templates, static files, endpoints from routers and session middleware
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

mongo_engine.init_app(app)
render_engine.init_app(app)
signals_engine.init_app(app)

# Adding middlewares
app.add_middleware(SessionMiddleware, secret_key=generate_salt())



app.include_router(main.router)
app.include_router(users.router, prefix="/users")
app.include_router(groups.router, prefix="/groups")

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



if __name__ == "__main__":
    from uvicorn import run
    run(app, port=8080)