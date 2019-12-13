from fastapi import APIRouter
from starlette.requests import Request


def make_router(database, schemas, operations, application, templates, session):
    router = APIRouter()

    @router.get("/")
    async def homepage(request: Request):
        return templates.TemplateResponse("homepage.html", {"request": request})

    return router
