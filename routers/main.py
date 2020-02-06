from typing import Callable, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request

from extensions.rendering import get_render
from extensions.signals import get_message_flashes
from models import User, Node, Group
from pprint import pformat

from .dependencies import get_session_email, get_current_user
from pydantic import EmailStr

router = APIRouter()


@router.get("/")
async def home(request: Request, flashes: list = Depends(get_message_flashes), render: Callable = Depends(get_render)):
    context = {"request": request, "flashes": flashes}
    session_email: Optional[EmailStr] = None
    current_user: Optional[User] = None
    try:
        session_email = await get_session_email(request=request)
        current_user = await get_current_user(request=request)
        # context["current_user"] = current_user = User.parse_obj(await User.collection.find_one({"email": email}))
    except HTTPException:
        pass
    if session_email is not None:
        context["session_email"] = session_email
        context["current_user"] = current_user
        context["extra"] = pformat(await current_user.unshallow(level=3))
        # nodes: List[Node] = [ Node.parse_obj(item) for item in await Group.collection.aggregate([
        #     {"$match": {"_id": {"$in": [g.id for g in current_user.groups]}}},
        #     {"$unwind": {"path": "$nodes"}},
        #     {"$group": {"_id": None, "all_nodes": {"$push": "$nodes._id"}}},
        #     {"$lookup": {"from": "nodes", "localField": "all_nodes", "foreignField": "_id", "as": "nodes"}},
        #     {"$unwind": {"path": "$nodes"}},
        #     {"$replaceRoot": {"newRoot": "$nodes"}},
        #     {"$lookup": {"from": "fs.files", "localField": "contents._id", "foreignField": "_id", "as": "contents"}},
        #     {"$addFields": {"contents": "$contents.metadata"}},
        # ]).to_list(length=500)]
        # # pprint(nodes)
        # context["user_s_nodes"] = nodes
        # if len(nodes) > 0:
        #     context["user_has_nodes"] = True
        return render("homepage.html", context)
    else:
        return render("landing.html", context)
