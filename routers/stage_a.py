from fastapi import APIRouter, Form, Depends  # , File, UploadFile
from starlette.requests import Request
from starlette.responses import RedirectResponse
from helpers import flash, get_message_flashes


def make_router(mc, application, templates):
    router = APIRouter()
    db_session = mc.db_session

    @router.get("/")
    async def home(request: Request, flashes: list = Depends(get_message_flashes)):
        try:
            username = request.session["authenticated_username"]
            with db_session:
                current_user = mc.User.operations.fetch(dict(username=username)).to_dict()
        except KeyError:
            current_user = None
        context = {}
        context.update({"request": request, "current_user": current_user, "flashes": flashes})
        return templates.TemplateResponse("homepage.html", context)

    @router.get("/signout")
    async def signout(request: Request):
        try:
            del request.session["authenticated_username"]
        except KeyError:
            pass
        return RedirectResponse(url="/", status_code=303)

    @router.post("/signin")
    async def signin(request: Request, username: str = Form(...), password: str = Form(...)):
        with db_session:
            u = mc.User.operations.fetch(dict(username=username))
            if u is not None and u.authenticate(password):
                request.session["authenticated_username"] = username
            else:
                try:
                    del request.session["authenticated_username"]
                except KeyError:
                    pass
                flash(request, "Utente non riconosciuto.", "warning")
                return RedirectResponse(url="/", status_code=303)
        return RedirectResponse(url="/", status_code=303)

    @router.get("/signup")
    async def signup(request: Request, flashes: list = Depends(get_message_flashes)):
        return templates.TemplateResponse("signup.html", {"request": request, "flashes": flashes})

    @router.post("/signup")
    async def signup(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...),
                     repassword: str = Form(...)):
        if password == repassword:
            from popy import TransactionIntegrityError
            try:
                with db_session:
                    mc.User.operations.create(dict(username=username, email=email, password=password))
                flash(request, "Utente creato con successo.", "success")
                return RedirectResponse(url="/", status_code=303)
            except TransactionIntegrityError:
                flash(request, "Non è stato possibile creare l'utente. Forse un duplicato?", "warning")
                return RedirectResponse(url="/signup", status_code=303)
        else:
            flash(request, "Le password devono coincidere.", "warning")
            return RedirectResponse(url="/signup", status_code=303)

    @router.get("/profile")
    async def profile(request: Request, flashes: list = Depends(get_message_flashes)):
        try:
            username = request.session["authenticated_username"]
            with db_session:
                current_user = mc.User.operations.fetch(dict(username=username)).to_dict()
        except KeyError:
            current_user = None
        user_groups = all_groups = []
        if current_user:
            with db_session:
                public_groups = list(mc.Group.operations.select({"public": True}))
                active_groups = list(mc.User.operations.fetch(dict(username=username)).groups)
                user_groups = [group.to_dict() for group in active_groups]
                other_groups = [group.to_dict() for group in public_groups if group not in active_groups]
        context = {}
        context.update({"request": request, "current_user": current_user, "flashes": flashes, "user_groups": user_groups, "other_groups": other_groups})
        return templates.TemplateResponse("profile.html", context)



    @router.post("/subscribe")
    async def subscribe(request: Request, group_id: int = Form(...)):
        with db_session:
            group = mc.Group.operations.fetch({"id":group_id})
            username = request.session["authenticated_username"]
            user = mc.User.operations.fetch(dict(username=username))
            user.groups.add(group)
        return RedirectResponse(url="/", status_code=303)

    @router.post("/unsubscribe")
    async def unsubscribe(request: Request, group_id: int = Form(...)):
        with db_session:
            group = mc.Group.operations.fetch({"id":group_id})
            username = request.session["authenticated_username"]
            user = mc.User.operations.fetch(dict(username=username))
            user.groups.remove(group)
        return RedirectResponse(url="/", status_code=303)

    @router.post("/change_fullname")
    async def change_fullname(request: Request, fullname: str = Form(None)):
        with db_session:
            username = request.session["authenticated_username"]
            user = mc.User.operations.fetch(dict(username=username))
            if fullname is not None:
                user.fullname = fullname
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
