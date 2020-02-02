from typing import Callable, List, Optional

from fastapi import APIRouter, Depends
from starlette.requests import Request

from extensions.rendering import get_render
from extensions.signals import get_message_flashes
from models import User, Node, Group
from pprint import pprint

router = APIRouter()


@router.get("/")
async def home(request: Request, flashes: list = Depends(get_message_flashes), render: Callable = Depends(get_render)):
    user_list = await User.collection.find().to_list(length=500)
    context = {"request": request, "flashes": flashes, "context": str(user_list)}
    current_user: Optional[User] = None
    try:
        email = request.session["authenticated_email"]
        context["current_user"] = current_user = User.parse_obj(await User.collection.find_one({"email": email}))
    except KeyError:
        context["current_user"] = current_user = None
    if current_user:
        nodes: List[Node] = [ Node.parse_obj(item) for item in await Group.collection.aggregate([
            {"$match": {"_id": {"$in": [g.id for g in current_user.groups]}}},
            {"$unwind": {"path": "$nodes"}},
            {"$group": {"_id": None, "all_nodes": {"$push": "$nodes._id"}}},
            {"$lookup": {"from": "nodes", "localField": "all_nodes", "foreignField": "_id", "as": "nodes"}},
            {"$unwind": {"path": "$nodes"}},
            {"$replaceRoot": {"newRoot": "$nodes"}},
            {"$lookup": {"from": "fs.files", "localField": "contents._id", "foreignField": "_id", "as": "contents"}},
            {"$addFields": {"contents": "$contents.metadata"}},
        ]).to_list(length=500)]
        # pprint(nodes)
        context["user_s_nodes"] = nodes
        if len(nodes) > 0:
            context["user_has_nodes"] = True
    return render("homepage.html", context)
