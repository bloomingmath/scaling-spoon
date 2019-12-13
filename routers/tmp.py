from fastapi import APIRouter, File, UploadFile, Form
from starlette.requests import Request


def make_router(database, schemas, operations, application, templates, session):
    router = APIRouter()

    @router.post("/upload")
    async def upload(short: str = Form(...), filetype: str = Form(...), file: UploadFile = File(...), long: str = Form(None)):
        with session:
            new_content = operations.create.content(database, {"short": short, "filetype": filetype, "long": long})
            serial = new_content.serial
            filetype = new_content.filetype
            open(f"static/contents/{serial}.{filetype}", "wb").write(await file.read())
            return {"new_content": new_content.to_dict()}

    return router
