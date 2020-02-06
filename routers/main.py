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
    try:
        session_email = request.session.get("authenticated_email", "")
        current_user: Optional[User] = await User.find_one({"email": session_email})
        assert current_user is not None
        context["session_email"] = session_email
        context["current_user"] = current_user
        context["nodes"] = await Node.find_by_groups(current_user.groups)
        return render("homepage.html", context)
    except AssertionError:
        return render("landing.html", context)
