from fastapi import APIRouter, Form, Depends  # , File, UploadFile
from starlette.requests import Request
from starlette.responses import RedirectResponse
from helpers import flash, get_message_flashes
from models import User
from extensions import get_render, get_database, AsyncIOMotorDatabase
from typing import Callable

router = APIRouter()


@router.get("/")
async def home(request: Request, flashes: list = Depends(get_message_flashes),
               db: AsyncIOMotorDatabase = Depends(get_database), render: Callable = Depends(get_render)):
    context = {"request": request, "flashes": flashes}
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
    return render("homepage.html", context)
