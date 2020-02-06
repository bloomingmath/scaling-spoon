from typing import Callable, Optional

from fastapi import APIRouter, Form, Depends
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import RedirectResponse

from extensions.rendering import get_render
from extensions.security import get_password_hash
from extensions.signals import flash, get_message_flashes
from models import User, Group
from schemas import SignupForm, LoginForm
from .dependencies import get_current_user
from .dependencies import get_session_email

router = APIRouter()


# GET routes
@router.get("/login")
async def login_get(request: Request,
                    flashes: list = Depends(get_message_flashes),
                    render: Callable = Depends(get_render)):
    return render("login.html", {"request": request, "flashes": flashes})


@router.get("/logout")
async def logout(request: Request):
    try:
        del request.session["authenticated_email"]
    except KeyError:
        pass
    return RedirectResponse(url="/", status_code=303)


@router.get("/profile")
async def profile(request: Request,
                  flashes: list = Depends(get_message_flashes),
                  current_user: User = Depends(get_current_user),
                  render: Callable = Depends(get_render)):
    context = {"flashes": flashes, "request": request, "current_user": current_user,
               "user_groups": await Group.find_by_user(current_user),
               "other_groups": await Group.find_by_not_user(current_user)}
    return render("profile.html", context)


@router.get("/signup")
async def signup_get(request: Request, flashes: list = Depends(get_message_flashes),
                     render: Callable = Depends(get_render)):
    return render("signup.html", {"request": request, "flashes": flashes})


# POST routes
@router.post("/change_username")
async def user_change_username(current_user_email: str = Depends(get_session_email), username: str = Form("")):
    await User.find_one_and_set(
        filter={"email": current_user_email},
        set={"username": username},
    )
    return RedirectResponse(url="/", status_code=303)


@router.post("/change_password")
async def user_change_password(request: Request, current_user: User = Depends(get_current_user), email: str = Form(""),
                               old_password: str = Form(...), password: str = Form(...),
                               password_confirmation: str = Form(...)):
    try:
        assert current_user.email == email
        assert current_user.authenticate(old_password)
        assert password == password_confirmation
        await User.find_one_and_set(
            filter={"email": current_user.email},
            set={"password_hash": get_password_hash(password)},
        )
    except:
        flash(request, "Non è stato possibile modificare la password.", "warning")
    return RedirectResponse(url="/", status_code=303)


@router.post("/login")
async def login_post(request: Request, login_form: LoginForm = Depends()):
    try:
        user: Optional[User] = await User.find_one({"email": login_form.email})
        assert user.authenticate(login_form.password)
        request.session["authenticated_email"] = user.email
    except (ValidationError, KeyError, AttributeError, AssertionError):
        try:
            del request.session["authenticated_email"]
        except KeyError:
            pass
        flash(request, "Utente non riconosciuto.", "warning")
    return RedirectResponse(url="/", status_code=303)


@router.post("/signup")
async def signup_post(request: Request, signup_form: SignupForm = Depends(SignupForm)):
    user: Optional[User] = await User.find_one({"email": signup_form.email})
    if user is None:
        await User.insert_one({
            "email": signup_form.email,
            "password_hash": get_password_hash(signup_form.password),
            "username": "",
            "groups": [],
        })
        flash(request, "Utente creato con successo.", "success")
    else:
        flash(request, "Non è stato possibile creare l'utente. Forse un duplicato?", "warning")
    return RedirectResponse(url="/", status_code=303)


@router.post("/subscribe")
async def user_subscribe(current_user: str = Depends(get_current_user), short: str = Form("")):
    return RedirectResponse(url="/", status_code=303)


@router.post("/unsubscribe")
async def user_unsubscribe(current_user: str = Depends(get_current_user), short: str = Form("")):
    return RedirectResponse(url="/", status_code=303)
