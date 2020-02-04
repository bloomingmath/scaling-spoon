from os import getenv

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

from extensions.mongo import mongo_engine
from extensions.rendering import render_engine, get_render
from extensions.security import generate_salt
from extensions.signals import signals_engine
from routers import users, main, groups, contents, admin

load_dotenv()
FASTAPI_ENVIRONMENT = getenv("FASTAPI_ENVIRONMENT", "development")
MONGODB_URI = getenv("MONGODB_URI", "mongodb://localhost:27017")

# Create fastapi application with rendering engine, motor mongodb connection, static files and signaling system
app = FastAPI(title="Scaling spoon")

app.mount("/static", StaticFiles(directory="static"), name="static")
# mongo_engine.init_app(app)
mongo_engine.init_app(app, uri=MONGODB_URI, env=FASTAPI_ENVIRONMENT)
render_engine.init_app(app, template_directory="templates")
signals_engine.init_app(app)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    render = get_render()
    return render("request_validation_error.html", {"request": request, "exception": str(exc)})


@app.exception_handler(Exception)
async def server_error_handler(request, exc):
    from datetime import datetime
    from traceback import format_exc
    render = get_render()
    with open("server_error.log", "a") as f:
        f.write("\n" + "#" * 40 + "\n")
        f.write(f"UNHANDLED ERROR {datetime.now().ctime()}\n\n")
        for line in format_exc().splitlines():
            f.write(line + "\n")
        f.write("#" * 40 + "\n")
    return render("server_error.html", {"request": request})


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
app.include_router(admin.router, prefix="/admin")

if __name__ == "__main__":
    from uvicorn import run

    run(app, port=8080)
