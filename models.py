from __future__ import annotations

from typing import Optional, List

from bson import ObjectId
from pydantic import BaseModel, EmailStr, root_validator, ValidationError

from db import AsyncIOMotorDatabase
from helpers.security import get_password_hash, generate_salt, verify_password
from schemas import SignupForm, UpdateUserModel, ForceUnset




class DbModel(BaseModel):
    id: Optional[str]

    @root_validator(pre=True)
    def set_id(cls, values):
        if values.get("_id") is not None:
            values["id"] = str(values["_id"])
        return values


class Group(DbModel):
    short: str

    @classmethod
    async def browse(cls, db: AsyncIOMotorDatabase) -> List[Group]:
        return [cls.from_orm(item) async for item in db["groups"].find({})]


class User(DbModel):
    email: EmailStr
    salt: str
    password_hash: str
    username: Optional[str] = None
    groups: Optional[List[Group]] = []

    def authenticate(self, password: str) -> bool:
        return verify_password(self.salt + password, self.password_hash)

    @classmethod
    async def create(cls, db: AsyncIOMotorDatabase, signup_form: SignupForm) -> User:
        email = signup_form.email
        user = await db["users"].find_one({"email": email})
        if user is None:
            salt = generate_salt()
            password_hash = get_password_hash(salt + signup_form.password)
            insert_result = await db["users"].insert_one({"email": email, "salt": salt, "password_hash": password_hash})
            return await db["users"].find_one({"_id": insert_result.inserted_id})
        else:
            raise ValueError("Email is already in use.")

    @classmethod
    async def read(cls, db: AsyncIOMotorDatabase, **kwargs) -> Optional[User]:
        user = await db["users"].find_one(kwargs)
        if user is not None:
            return cls.parse_obj(user)
        else:
            return None

    @classmethod
    async def update(cls, db: AsyncIOMotorDatabase, update_user_model: UpdateUserModel) -> None:
        filter = {"_id": ObjectId(update_user_model.id)}
        update_set = {key: value for key, value in update_user_model.dict(exclude={"id"}, exclude_none=True).items() if
                      not isinstance(value, ForceUnset)}
        update_unset = {key: "" for key, value in update_user_model.dict().items() if isinstance(value, ForceUnset)}
        update = {}
        if update_set: update["$set"] = update_set
        if update_unset: update["$unset"] = update_unset
        await db["users"].find_one_and_update(filter, update)
