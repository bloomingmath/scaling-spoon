from __future__ import annotations

from typing import Optional, List

from bson import ObjectId
from pydantic import BaseModel, EmailStr, root_validator

from helpers.security import get_password_hash, generate_salt, verify_password
from schemas import SignupForm, UpdateUserModel, ForceUnset
from extensions import AsyncIOMotorDatabase, get_extra_collection


class DbModel(BaseModel):
    id: str

    @root_validator(pre=True)
    def set_id(cls, values):
        if isinstance(values.get("_id"), ObjectId):
            values["id"] = str(values["_id"])
        elif isinstance(values.get("_id"), str):
            values["id"] = values["_id"]
        return values

    def __hash__(self):
        return hash(id)


class Group(DbModel):
    short: str

    @classmethod
    async def browse(cls, db: AsyncIOMotorDatabase) -> List[Group]:
        return [cls.parse_obj(item) async for item in db["groups"].find({})]

    def __getitem__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            raise KeyError


class User(DbModel):
    email: EmailStr
    password_hash: str
    username: Optional[str] = None
    groups: Optional[List[Group]] = []

    def authenticate(self, password: str) -> bool:
        return verify_password(password, self.password_hash)

    @classmethod
    async def create(cls, db: AsyncIOMotorDatabase, signup_form: SignupForm) -> User:
        email = signup_form.email
        user = await db["users"].find_one({"email": email})
        if user is None:
            password_hash = get_password_hash(signup_form.password)
            insert_result = await db["users"].insert_one({"email": email, "password_hash": password_hash})
            return await db["users"].find_one({"_id": insert_result.inserted_id})
        else:
            raise ValueError("Email is already in use.")

    @classmethod
    async def read(cls, db: AsyncIOMotorDatabase, **kwargs) -> Optional[User]:
        users = get_extra_collection(db, "users")
        user = await users.find_one(kwargs)
        print(user)
        if user is not None:
            return cls(**user)
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

