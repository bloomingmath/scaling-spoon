from typing import Callable

from fastapi import APIRouter, Form, Depends, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from extensions.rendering import get_render
from extensions.security import get_password_hash
from extensions.signals import flash, get_message_flashes
from models import User, Group
from schemas import SignupForm, LoginForm
from logging import info

router = APIRouter()


async def get_current_user_email(request: Request):
    try:
        return request.session["authenticated_email"]
    except KeyError:
        raise HTTPException(status_code=403, detail="User is not authenticated (email).")


async def get_current_admin(request: Request, session_email: str = Depends(get_current_user_email)) -> User:
    try:
        user = User.parse_obj(await User.collection.find_one({"email": session_email}))
        if user.is_admin:
            return user
        else:
            raise KeyError
    except KeyError:
        raise HTTPException(status_code=403, detail="You are not a valid admin.")


# @router.post("/change_username")
# async def change_username(current_user_email: str = Depends(get_current_user_email), username: str = Form("")):
#     await User.collection.find_one_and_update(
#         filter={"email": current_user_email},
#         update={"$set": {"username": username}}
#     )
#     return RedirectResponse(url="/", status_code=303)
#
#
# @router.post("/login")
# async def login_post(request: Request, login_form: LoginForm = Depends()):
#     user: User = User.parse_obj(await User.collection.find_one({"email": login_form.email}))
#     if user is not None and user.authenticate(login_form.password):
#         request.session["authenticated_email"] = user.email
#     else:
#         try:
#             del request.session["authenticated_email"]
#         except KeyError:
#             pass
#         flash(request, "Utente non riconosciuto.", "warning")
#     return RedirectResponse(url="/", status_code=303)
#
#
# @router.get("/logout")
# async def logout(request: Request):
#     try:
#         del request.session["authenticated_email"]
#     except KeyError:
#         pass
#     return RedirectResponse(url="/", status_code=303)


@router.get("/")
async def dashboard(request: Request,
                    flashes: list = Depends(get_message_flashes),
                    admin: User = Depends(get_current_admin),
                    render: Callable = Depends(get_render)):
    context = {"flashes": flashes, "request": request, "current_user": admin}
    return render("admin_dashboard.html", context)


@router.get("/users")
async def users(request: Request,
                flashes: list = Depends(get_message_flashes),
                admin: User = Depends(get_current_admin),
                render: Callable = Depends(get_render)):
    context = {"flashes": flashes, "request": request, "current_user": admin, "users": [
        User.parse_obj(user) for user in (await User.collection.find().to_list(length=500))
    ]}
    return render("admin_users.html", context)

# @router.get("/signup")
# async def signup_get(request: Request, flashes: list = Depends(get_message_flashes),
#                      render: Callable = Depends(get_render)):
#     return render("signup.html", {"request": request, "flashes": flashes})
#
#
# @router.post("/signup")
# async def signup_post(request: Request, signup_form: SignupForm = Depends(SignupForm)):
#     email = signup_form.email
#     user_dict = await User.collection.find_one({"email": email})
#     if user_dict is None:
#         password_hash = get_password_hash(signup_form.password)
#         await User.collection.insert_one({
#             "email": email,
#             "password_hash": password_hash,
#             "username": "",
#             "groups": [],
#         })
#         flash(request, "Utente creato con successo.", "success")
#     else:
#         flash(request, "Non è stato possibile creare l'utente. Forse un duplicato?", "warning")
#     return RedirectResponse(url="/", status_code=303)
