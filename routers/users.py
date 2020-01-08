from typing import Callable

from fastapi import APIRouter, Form, Depends, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from extensions import AsyncIOMotorDatabase, get_database, get_render, flash, get_message_flashes, get_extra_collection
from models import User, Group, ForceUnset
from schemas import SignupForm, LoginForm, UpdateUserModel

router = APIRouter()


async def get_current_user(request: Request, db: AsyncIOMotorDatabase = Depends(get_database)):
    try:
        email = request.session["authenticated_email"]
        return await User.read(db=db, email=email)
    except KeyError:
        raise HTTPException(status_code=403, detail="User is not authenticated")


@router.post("/change_username")
async def change_username(db: AsyncIOMotorDatabase = Depends(get_database),
                          current_user: User = Depends(get_current_user), username: str = Form(ForceUnset())):
    await User.update(db, UpdateUserModel(id=current_user.id, username=username))
    return RedirectResponse(url="/", status_code=303)


@router.post("/login")
async def login_post(request: Request, login_form: LoginForm = Depends(),
                     db: AsyncIOMotorDatabase = Depends(get_database)):
    user: User = await User.read(db, email=login_form.email)
    if user is not None and user.authenticate(login_form.password):
        request.session["authenticated_email"] = user.email
    else:
        try:
            del request.session["authenticated_email"]
        except KeyError:
            pass
        flash(request, "Utente non riconosciuto.", "warning")
    return RedirectResponse(url="/", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    try:
        del request.session["authenticated_email"]
    except KeyError:
        pass
    return RedirectResponse(url="/", status_code=303)


@router.get("/profile")
async def profile(request: Request, flashes: list = Depends(get_message_flashes),
                  db: AsyncIOMotorDatabase = Depends(get_database), current_user: User = Depends(get_current_user),
                  render: Callable = Depends(get_render)):
    context = {"flashes": flashes, "request": request, "current_user": current_user}
    all_groups = await Group.browse(db)
    user_groups = list(current_user.groups)
    other_groups = [group for group in all_groups if group not in current_user.groups]
    context.update({"user_groups": user_groups, "other_groups":other_groups})
    return render("profile.html", context)


@router.get("/signup")
async def signup_get(request: Request, flashes: list = Depends(get_message_flashes),
                     render: Callable = Depends(get_render)):
    return render("signup.html", {"request": request, "flashes": flashes})


@router.post("/signup")
async def signup_post(request: Request, signup_form: SignupForm = Depends(SignupForm),
                      db: AsyncIOMotorDatabase = Depends(get_database)):
    try:
        await User.create(db, signup_form)
        flash(request, "Utente creato con successo.", "success")
    except ValueError:
        flash(request, "Non è stato possibile creare l'utente. Forse un duplicato?", "warning")
    return RedirectResponse(url="/", status_code=303)
