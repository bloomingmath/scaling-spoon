from fastapi import FastAPI
from importlib import import_module
from popy import generate_popy, db_session
from routers import frontend, tmp
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

database, schemas, operations = generate_popy(import_module("models"), provider="sqlite", filename="database.sqlite", create_db=True)

mainapp = FastAPI()

templates = Jinja2Templates(directory="templates")

mainapp.mount("/static", StaticFiles(directory="static"), name="static")

mainapp.include_router(frontend.make_router(database, schemas, operations, mainapp, templates, db_session))
mainapp.include_router(tmp.make_router(database, schemas, operations, mainapp, templates, db_session), prefix="/tmp")

# app.include_router(routers.admin_api.make_router(db), tags=["admin-api"], prefix="/api/admin")
