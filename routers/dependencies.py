from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException
from starlette.requests import Request
from logging import info, error
from models import User
from pydantic import EmailStr, ValidationError


async def get_session_email(request: Request) -> EmailStr:
    try:
        v = validate_email(request.session["authenticated_email"])
        return v["email"]  # replace with normalized form
    except (KeyError, EmailNotValidError):
        raise HTTPException(status_code=403,
                            detail="L'utente non è identificato (non se ne conosce l'indirizzo email).")


async def get_current_user(request: Request) -> User:
    try:
        email = await get_session_email(request=request)
        db_user = await User.collection.find_one({"email": email})
        if db_user is None:
            raise HTTPException(status_code=403,
                            detail="L'utente non è identificato (l'indirizzo email non è nel database).")
        user = User.parse_obj(db_user)
        return user
    except ValidationError:
        error(f"Could not parse db_user: {db_user}")
        raise HTTPException(status_code=403, detail="L'utente non è identificato (una incongruenza con i dati registrati nel database).")
