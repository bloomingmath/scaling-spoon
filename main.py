from fastapi import FastAPI
from importlib import import_module
from popy import generate_models_dict, db_session
from routers import frontend, stage_a
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

mdict = generate_models_dict(import_module("models"), provider="sqlite", filename="database.sqlite", create_db=True)

mainapp = FastAPI()

templates = Jinja2Templates(directory="templates")

mainapp.mount("/static", StaticFiles(directory="static"), name="static")

mainapp.include_router(frontend.make_router(mdict, mainapp, templates, db_session))
mainapp.include_router(stage_a.make_router(mdict, mainapp, templates, db_session), prefix="/tmp")

# app.include_router(routers.admin_api.make_router(db), tags=["admin-api"], prefix="/api/admin")
