from typing import Callable

from fastapi import APIRouter, Form, Depends, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from extensions.rendering import get_render
from extensions.security import get_password_hash
from extensions.signals import flash, get_message_flashes
from models import User, Group, Node, DBRef
from schemas import SignupForm, LoginForm
from logging import info
from pprint import pformat, pprint

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
    context["users_list"] = [await User.parse_obj(db_user).unshallow(level=3) for db_user in
                             await User.collection.find().to_list(length=500)]
    context["groups_list"] = [
        await Group.parse_obj(db_group).unshallow(level=2) for db_group in
        await Group.collection.find().to_list(length=500)
    ]
    context["nodes_list"] = [
        await Node.parse_obj(db_node).unshallow(level=1) for db_node in
        await Node.collection.find().to_list(length=500)
    ]
    pprint(context)
    return render("admin_dashboard.html", context)


@router.post("/reset_password")
async def admin_reset_password(request: Request, user_email: str = Form(...), admin: User = Depends(get_current_admin)):
    await User.collection.find_one_and_update(
        filter={"email": user_email},
        update={"$set": {"password_hash": get_password_hash("pass")}}
    )
    return RedirectResponse(url="/", status_code=303)


@router.post("/toggle_block")
async def admin_toggle_block(request: Request, user_email: str = Form(...), admin: User = Depends(get_current_admin)):
    db_user = await User.collection.find_one({"email": user_email})
    if db_user is None:
        flash(request, f"L'utente {user_email} non esiste.", "warning")
    else:
        user = User.parse_obj(db_user)
        await User.collection.find_one_and_update(
            filter={"email": user_email},
            update={"$set": {"is_blocked": (False if user.is_blocked else True)}}
        )
    return RedirectResponse(url="/", status_code=303)


@router.post("/create_group")
async def admin_create_group(request: Request, short: str = Form(...), admin: User = Depends(get_current_admin)):
    db_group = await Group.collection.find_one({"short": short})
    if db_group is not None:
        flash(request, f"Il gruppo {short} esiste già.", "warning")
    else:
        await Group.collection.insert_one({
            "short": short,
            "nodes": [],
        })
    return RedirectResponse(url="/", status_code=303)


@router.post("/create_user")
async def admin_create_user(request: Request, user_email: str = Form(...), admin: User = Depends(get_current_admin)):
    db_user = await User.collection.find_one({"email": user_email})
    if db_user is not None:
        flash(request, f"L'utente {user_email} esiste già.", "warning")
    else:
        await User.collection.insert_one({
            "email": user_email,
            "password_hash": get_password_hash("pass"),
            "username": "",
            "groups": [],
        })
    return RedirectResponse(url="/", status_code=303)


@router.post("/toggle_node")
async def admin_toggle_node(node_short: str = Form(...), group_short: str = Form(...),
                            admin: User = Depends(get_current_admin)):
    group = Group.parse_obj(await Group.collection.find_one({"short": group_short}))
    node_ref = DBRef.from_orm(Node.parse_obj(await Node.collection.find_one({"short": node_short})))
    if node_ref in group.nodes:
        nodes = [ref for ref in group.nodes if ref != node_ref]
    else:
        nodes = [node_ref] + group.nodes
    await Group.collection.find_one_and_update(
        filter={"short": group_short},
        update={"$set": {"nodes": nodes}}
    )
    return RedirectResponse(url="/", status_code=303)


@router.post("/toggle_group")
async def admin_toggle_group(user_email: str = Form(...), group_short: str = Form(...),
                            admin: User = Depends(get_current_admin)):
    group = Group.parse_obj(await Group.collection.find_one({"short": group_short}))
    user = User.parse_obj(await User.collection.find_one({"email": user_email}))
    group_ref = DBRef.from_orm(group)
    if group_ref in user.groups:
        groups = [ref for ref in user.groups if ref != group_ref]
    else:
        groups = [group_ref] + user.groups
    await User.collection.find_one_and_update(
        filter={"email": user_email},
        update={"$set": {"groups": groups}}
    )
    return RedirectResponse(url="/", status_code=303)


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
