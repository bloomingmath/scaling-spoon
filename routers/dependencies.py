from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException, Depends
from starlette.requests import Request
from logging import info, error
from models import User
from pydantic import EmailStr, ValidationError
from typing import Optional


async def get_session_email(request: Request) -> EmailStr:
    try:
        v = validate_email(request.session["authenticated_email"])
        return v["email"]  # replace with normalized form
    except (KeyError, EmailNotValidError):
        raise HTTPException(status_code=403,
                            detail="L'utente non è identificato (non se ne conosce l'indirizzo email).")


async def get_current_user(request: Request, session_email: EmailStr = Depends(get_session_email)) -> User:
    user: Optional[User] = await User.find_one({"email": session_email})
    if user:
        return user
    else:
        raise HTTPException(status_code=403, detail="L'utente non è identificato.")


async def get_current_admin(request: Request, current_user: User = Depends(get_current_user)) -> User:
    if current_user.is_admin:
        return current_user
    else:
        raise HTTPException(status_code=403, detail="L'utente non è amministratore.")
