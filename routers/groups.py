from fastapi import APIRouter, Form, Depends  # , File, UploadFile
from starlette.requests import Request
from starlette.responses import RedirectResponse
from extensions import flash, get_message_flashes, get_database, AsyncIOMotorDatabase, get_extra_collection
from models import User, Group
from .users import get_current_user
from bson import ObjectId

router = APIRouter()


@router.post("/subscribe")
async def subscribe(request: Request, group_id: str = Form(...), current_user: User = Depends(get_current_user),
                    db: AsyncIOMotorDatabase = Depends(get_database)):
    groups = get_extra_collection(db, "groups")
    users = get_extra_collection(db, "users")
    group = Group.parse_obj(await groups.find_one({"_id": ObjectId(group_id)}))
    extended_groups = {group}.union(current_user.groups)
    await users.find_one_and_update({"_id": ObjectId(current_user.id)}, {"$set": {"groups": [group for group in extended_groups]}})
    return RedirectResponse(url="/", status_code=303)


@router.post("/unsubscribe")
async def unsubscribe(request: Request, group_id: int = Form(...)):
    group = mc.Group.operations.fetch({"id": group_id})
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
