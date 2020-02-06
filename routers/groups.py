from bson import ObjectId
from fastapi import APIRouter, Form, Depends  # , File, UploadFile
from starlette.responses import RedirectResponse

from models import Model, User
from .users import get_current_user

router = APIRouter()


@router.post("/subscribe")
async def subscribe(group_id: str = Form(...), current_user: User = Depends(get_current_user)):
    group_id = ObjectId(group_id)
    if group_id not in [ref.id for ref in current_user.groups]:
        current_user.groups.append(Model(id=group_id, collection_name="groups"))
        await User.collection.find_one_and_update({"_id": current_user.id}, {"$set": {"groups": current_user.groups}})
    return RedirectResponse(url="/", status_code=303)


@router.post("/unsubscribe")
async def unsubscribe(group_id: str = Form(...), current_user: User = Depends(get_current_user)):
    group_id = ObjectId(group_id)
    current_user.groups = [ref for ref in current_user.groups if ref.id != group_id]
    await User.collection.find_one_and_update({"_id": current_user.id}, {"$set": {"groups": current_user.groups}})
    return RedirectResponse(url="/", status_code=303)
