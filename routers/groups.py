from fastapi import APIRouter, Form, Depends  # , File, UploadFile
from starlette.requests import Request
from starlette.responses import RedirectResponse
from extensions.rendering import get_render
from extensions.mongo import get_motor, AsyncIoMotor
from models import User, Group
from .users import get_current_user
from bson import ObjectId

router = APIRouter()


@router.post("/subscribe")
async def subscribe(request: Request, group_id: str = Form(...), current_user: User = Depends(get_current_user),
                    motor: AsyncIoMotor = Depends(get_motor)):
    groups = motor["groups"]
    users = motor["users"]
    group = Group.parse_obj(await groups.find_one({"_id": ObjectId(group_id)}))
    extended_groups = {group}.union(current_user.groups)
    await users.find_one_and_update({"_id": ObjectId(current_user.id)}, {"$set": {"groups": [group for group in extended_groups]}})
    return RedirectResponse(url="/", status_code=303)


@router.post("/unsubscribe")
async def unsubscribe(request: Request, group_id: str = Form(...), current_user: User = Depends(get_current_user),
                    motor: AsyncIoMotor = Depends(get_motor)):
    groups = motor["groups"]
    users = motor["users"]
    group = Group.parse_obj(await groups.find_one({"_id": ObjectId(group_id)}))
    try:
        current_user.groups.remove(group)
    except ValueError:
        pass
    await users.find_one_and_update({"_id": ObjectId(current_user.id)}, {"$set": {"groups": current_user.groups}})
    return RedirectResponse(url="/", status_code=303)
