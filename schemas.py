from typing import Optional, Union

from fastapi import Form
from pydantic import BaseModel, EmailStr, root_validator, validator


class ForceUnset:
    pass


class SignupForm(BaseModel):
    email: EmailStr
    password: str
    password_confirmation: str

    def __init__(self, email: EmailStr = Form(...), password: str = Form(...), password_confirmation: str = Form(...)):
        super().__init__(email=email, password=password, password_confirmation=password_confirmation)
        # self.email = email
        # self.password = password
        # self.password_confirmation = password_confirmation

    @validator("password")
    def password_is_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Password can't be an empty string.")
        return value

    @root_validator
    def passwords_match(cls, values):
        pw1, pw2 = values.get("password"), values.get("password_confirmation")
        if pw1 != pw2:
            raise ValueError(f"Passwords do not match ({pw1} vs. {pw2}).")
        return values


class LoginForm(BaseModel):
    email: EmailStr
    password: str

    def __init__(self, email: EmailStr = Form(...), password: str = Form(...)):
        super().__init__(email=email, password=password)

    @validator("password")
    def password_is_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Password can't be an empty string.")
        return value


class UpdateUserModel(BaseModel):
    id: str
    password: Optional[str]
    username: Union[str, ForceUnset, None]

    class Config:
        arbitrary_types_allowed = True
