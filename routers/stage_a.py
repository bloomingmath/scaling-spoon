from fastapi import APIRouter, Form, Depends  # , File, UploadFile
from starlette.requests import Request
from starlette.responses import RedirectResponse
from helpers import flash, get_message_flashes
from models import User
from db.mongodb import get_database, AsyncIOMotorDatabase



def make_router(mc, application, templates):
    router = APIRouter()
    db_session = mc.db_session

    def get_authenticated_username(request: Request):
        """Dependency for current authenticated user in session."""
        return request.session.get("authenticated_username", None)

    def get_current_user(request: Request):
        username = request.session.get("authenticated_username", None)
        return mc.User.operations.fetch({"username": username})

    @router.get("/")
    async def home(request: Request, flashes: list = Depends(get_message_flashes), db: AsyncIOMotorDatabase = Depends(get_database)):
        context = {"request": request, "flashes": flashes}
        with db_session:
            try:
                email = request.session["authenticated_email"]
                current_user = await User.read(db=db, email=email)
                context["current_user"] = current_user
                # if current_user is not None:
                #     user_s_nodes = [ node.to_dict() for node in set([ node for group in current_user.groups for node in group.nodes ]) ]
                #     context["user_s_nodes"] = user_s_nodes
                #     context["user_has_nodes"] = len(user_s_nodes) > 0
            except KeyError:
                context["current_user"] = None
        return templates.TemplateResponse("homepage.html", context)



    @router.post("/subscribe")
    async def subscribe(request: Request, group_id: int = Form(...)):
        with db_session:
            current_user = get_current_user(request)
            group = mc.Group.operations.fetch({"id":group_id})
            current_user.groups.add(group)
        return RedirectResponse(url="/", status_code=303)

    @router.post("/unsubscribe")
    async def unsubscribe(request: Request, group_id: int = Form(...)):
        with db_session:
            group = mc.Group.operations.fetch({"id":group_id})
            current_user = get_current_user(request)
            current_user.groups.remove(group)
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