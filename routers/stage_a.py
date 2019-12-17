from fastapi import APIRouter, File, UploadFile, Form
from starlette.requests import Request
from starlette.responses import RedirectResponse
import forge


def make_router(mc, application, templates):
    router = APIRouter()
    db_session = mc.db_session

    @router.get("/")
    async def home(request: Request):
        try:
            username = request.session["authenticated_username"]
            with db_session:
                current_user = mc.User.operations.fetch(dict(username=username)).to_dict()
        except:
            current_user = None
        return templates.TemplateResponse("homepage.html", {"request": request, "current_user": current_user})

    @router.get("/signout")
    async def signout(request: Request):
        request.session["authenticated_username"] = None
        return RedirectResponse(url="/", status_code=303)

    @router.post("/signin")
    async def signin(request: Request, username: str = Form(...), password: str = Form(...)):
        with db_session:
            u = mc.User.operations.fetch(dict(username=username))
            if u is not None and u.authenticate(password):
                request.session["authenticated_username"] = username
            else:
                request.session["authenticated_username"] = None
                raise Exception("User were not authenticated.")
        return RedirectResponse(url="/", status_code=303)

    @router.get("/signup")
    async def signup(request: Request):
        return templates.TemplateResponse("signup.html", {"request": request})

    @router.post("/signup")
    async def signup(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...),
                     repassword: str = Form(...)):
        if password == repassword:
            with db_session:
                mc.User.operations.create(dict(username=username, email=email, password=password))
        else:
            raise ValueError("Passwords must match")
        return RedirectResponse(url="/", status_code=303)

    # @router.post("/upload")
    # async def upload(short: str = Form(...), filetype: str = Form(...), file: UploadFile = File(...),
    #                  long: str = Form(None)):
    #     with db_session:
    #         Content = mdict["Content"]
    #         new_content = Content.operations.create(create_info={"short": short, "filetype": filetype, "long": long})
    #         serial = new_content.serial
    #         filetype = new_content.filetype
    #         open(f"static/contents/{serial}.{filetype}", "wb").write(await file.read())
    #         return {"new_content": new_content.to_dict()}
    #
    # # @router.post("/admin/create/group")
    # # async def admin_create_group(create_info: mdict["Group"].schemas.create):
    # #     Group = mdict["Group"]
    # #     with db_session:
    # #         x = Group.operations.create(create_info.dict())
    # #     return {}
    # admin_endopints = []
    # for model_name, model in mdict.items():
    #     for operation_name, operation in model.operations.items():
    #         async def admin_endpoint(**kwargs):
    #             print(model.operations[str(operation_name)](**{ key: value.dict() for key, value in kwargs.items() }))
    #             print("ADIM ENDPOINT", kwargs["create_info"])
    #             return {}
    #
    #         admin_endpoint = forge.copy(operation)(admin_endpoint)
    #         try:
    #             admin_endpoint = forge.modify("create_info", type=model.schemas.create)(admin_endpoint)
    #         except:
    #             pass
    #         try:
    #             admin_endpoint = forge.modify("get_info", type=model.schemas.get)(admin_endpoint)
    #         except:
    #             pass
    #         try:
    #             admin_endpoint = forge.modify("select_info", type=model.schemas.select)(admin_endpoint)
    #         except:
    #             pass
    #         try:
    #             admin_endpoint = forge.modify("update_info", type=model.schemas.update)(admin_endpoint)
    #         except:
    #             pass
    #
    #         # print( forge.fsignature(func))
    #         admin_endpoint.__name__ = f"admin {operation_name} {model_name.lower()}"
    #         admin_endopints.append({"path": f"/admin/{operation_name}/{model_name.lower()}", "endpoint": admin_endpoint})
    #         # print( forge.fsignature(admin_endpoint) )
    # for dend in admin_endopints:
    #     router.add_api_route(dend["path"], dend["endpoint"], methods=["POST"])

    return router
