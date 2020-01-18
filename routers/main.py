from typing import Callable

from fastapi import APIRouter, Depends
from starlette.requests import Request

from extensions.rendering import get_render
from extensions.signals import get_message_flashes
from models import User

router = APIRouter()


@router.get("/")
async def home(request: Request, flashes: list = Depends(get_message_flashes), render: Callable = Depends(get_render)):
    context = {"request": request, "flashes": flashes}
    try:
        email = request.session["authenticated_email"]
        current_user: User = User.parse_obj(await User.collection.find_one({"email": email}))
        context["current_user"] = current_user
    except KeyError:
        context["current_user"] = None
    return render("homepage.html", context)
