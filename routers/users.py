from fastapi import APIRouter, Form, Depends, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from db.mongodb import AsyncIOMotorDatabase, get_database
from helpers import flash, get_message_flashes
from main import templates
from models import User
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
                          current_user: User = Depends(get_current_user), username: str = Form(...)):
    print("cu", current_user)
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
                  db: AsyncIOMotorDatabase = Depends(get_database), current_user: User = Depends(get_current_user)):
    context = {"flashes": flashes, "request": request, "current_user": current_user}
    # public_groups = list(mc.Group.operations.select({"public": True}))
    # active_groups = list(current_user.groups)
    # user_groups = [group.to_dict() for group in active_groups]
    # other_groups = [group.to_dict() for group in public_groups if group not in active_groups]
    # context.update({"user_groups": user_groups, "other_groups": other_groups})
    return templates.TemplateResponse("profile.html", context)


@router.get("/signup")
async def signup_get(request: Request, flashes: list = Depends(get_message_flashes)):
    return templates.TemplateResponse("signup.html", {"request": request, "flashes": flashes})


@router.post("/signup")
async def signup_post(request: Request, signup_form: SignupForm = Depends(SignupForm),
                      db: AsyncIOMotorDatabase = Depends(get_database)):
    await User.create(db, signup_form)
    flash(request, "Utente creato con successo.", "success")
    return RedirectResponse(url="/", status_code=303)
