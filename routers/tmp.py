from fastapi import APIRouter, File, UploadFile, Form
from starlette.requests import Request


def make_router(database, schemas, operations, application, templates, session):
    router = APIRouter()

    @router.get("/")
    async def temporary(request: Request):
        with session:
            contents_list = list( (content.to_dict()["short"], "/static/contents/{}.{}".format(content.to_dict()["serial"], content.to_dict()["filetype"])) for content in operations.select.content(database, {}))
        return templates.TemplateResponse("mirabilia.html", {"request": request, "contents_list": contents_list})


    @router.post("/upload")
    async def upload(short: str = Form(...), filetype: str = Form(...), file: UploadFile = File(...), long: str = Form(None)):
        with session:
            new_content = operations.create.content(database, {"short": short, "filetype": filetype, "long": long})
            serial = new_content.serial
            filetype = new_content.filetype
            open(f"static/contents/{serial}.{filetype}", "wb").write(await file.read())
            return {"new_content": new_content.to_dict()}

    return router
