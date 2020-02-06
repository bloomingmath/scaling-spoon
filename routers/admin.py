from typing import Callable

from fastapi import APIRouter, Form, Depends, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from extensions.rendering import get_render
from extensions.security import get_password_hash
from extensions.signals import flash, get_message_flashes
from models import User, Group, Node, Content, Model, get_id
from schemas import SignupForm, LoginForm
from logging import info
from pprint import pformat, pprint
from .dependencies import get_current_admin
from pydantic import EmailStr

router = APIRouter()


@router.get("/")
async def dashboard(request: Request,
                    flashes: list = Depends(get_message_flashes),
                    admin: User = Depends(get_current_admin),
                    render: Callable = Depends(get_render)):
    context = {"flashes": flashes, "request": request, "current_user": admin}
    context["users_list"] = await User.find_with_complete_groups()
    context["groups_list"] = await Group.find_with_complete_nodes()
    context["nodes_list"] = await Node.find_with_complete_contents()
    return render("admin_dashboard.html", context)


@router.post("/create_user")
async def admin_create_user(request: Request, user_email: EmailStr = Form(...),
                            admin: User = Depends(get_current_admin)):
    user = await User.find_one({"email": user_email})
    if user:
        flash(request, f"L'utente {user_email} esiste già.", "warning")
    else:
        await User.insert_one({
            "email": user_email,
            "password_hash": get_password_hash("pass"),
            "username": "",
            "groups": [],
        })
    return RedirectResponse(url="/", status_code=303)


@router.post("/create_group")
async def admin_create_group(request: Request, short: str = Form(...), admin: User = Depends(get_current_admin)):
    group = await Group.find_one({"short": short})
    if group:
        flash(request, f"Il gruppo {short} esiste già.", "warning")
    else:
        await Group.insert_one({
            "short": short,
            "nodes": [],
        })
    return RedirectResponse(url="/", status_code=303)


@router.post("/create_node")
async def admin_create_node(request: Request, node_short: str = Form(...), admin: User = Depends(get_current_admin)):
    node = await Node.find_one({"short": node_short})
    print("Node is:", node)
    if node:
        flash(request, f"L'argomento {node_short} già esiste.", "warning")
    else:
        await Node.insert_one({
            "short": node_short,
            "contents": [],
        })
    return RedirectResponse(url="/", status_code=303)


@router.post("/delete_node")
async def admin_delete_node(request: Request, node_short: str = Form(...), admin: User = Depends(get_current_admin)):
    node = Node.find_one({"short": node_short})
    if node:
        await Node.delete_one({"short": node_short})
    else:
        flash(request, f"L'argomento {node_short} non esiste.")
    return RedirectResponse(url="/", status_code=303)


@router.post("/reset_password")
async def admin_reset_password(request: Request, user_email: str = Form(...), admin: User = Depends(get_current_admin)):
    await User.find_one_and_set(
        filter={"email": user_email},
        set={"password_hash": get_password_hash("pass")}
    )
    return RedirectResponse(url="/", status_code=303)


@router.post("/toggle_block")
async def admin_toggle_block(request: Request, user_email: EmailStr = Form(...),
                             admin: User = Depends(get_current_admin)):
    user = await User.find_one({"email": user_email})
    if user:
        await User.find_one_and_set(
            filter={"email": user_email},
            set={"is_blocked": (False if user.is_blocked else True)}
        )
    else:
        flash(request, f"L'utente {user_email} non esiste.", "warning")
    return RedirectResponse(url="/", status_code=303)


@router.post("/toggle_group")
async def admin_toggle_group(user_email: str = Form(...), group_short: str = Form(...),
                             admin: User = Depends(get_current_admin)):
    group = await Group.find_one({"short": group_short})
    user = await User.find_one({"email": user_email})
    if group.id in user.groups:
        user.groups.remove(group.id)
    else:
        user.groups.append(group.id)
    await User.find_one_and_set(
        filter={"email": user_email},
        set={"groups": user.groups}
    )
    return RedirectResponse(url="/", status_code=303)


@router.post("/toggle_node")
async def admin_toggle_node(node_short: str = Form(...), group_short: str = Form(...),
                            admin: User = Depends(get_current_admin)):
    group = await Group.find_one({"short": group_short})
    node = await Node.find_one({"short": node_short})
    if node.id in group.nodes:
        group.nodes.remove(node.id)
    else:
        group.nodes.append(node.id)
    await Group.find_one_and_set(
        filter={"short": group_short},
        set={"nodes": group.nodes}
    )
    return RedirectResponse(url="/", status_code=303)


@router.post("/toggle_content")
async def admin_toggle_content(node_short: str = Form(...), content_id_str: str = Form(...),
                               admin: User = Depends(get_current_admin)):
    node = await Node.find_one({"short": node_short})
    content_id = get_id(content_id_str)
    if content_id in node.contents:
        node.contents.remove(content_id)
    else:
        node.contents.append(content_id)
    await Node.find_one_and_set(
        filter={"short": node_short},
        set={"contents": node.contents}
    )
    print("Toggle content", node.contents)
    return RedirectResponse(url="/", status_code=303)
