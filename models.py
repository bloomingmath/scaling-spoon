from __future__ import annotations

from typing import Optional, List

from bson import ObjectId
from pydantic import BaseModel, EmailStr, root_validator

from new_extensions.security import get_password_hash, verify_password
from schemas import SignupForm, UpdateUserModel, ForceUnset
from new_extensions.mongo import AsyncIoMotor
from logging import debug

class DbModel(BaseModel):
    _id: Optional[str] = None

    # @root_validator(pre=True)
    # def set_id(cls, values):
    #     try:
    #         values["id"] = str(values["_id"])
    #         debug("setting id")
    #     except KeyError:
    #         pass
    #     return values
    #     try:
    #         values["id"] = str(values["_id"])
    #     except:
    #         return values
        # if isinstance(values.get("_id"), ObjectId):
        #     values["id"] = str(values["_id"])
        # elif isinstance(values.get("_id"), str):
        #     values["id"] = values["_id"]
        # return values

    def __hash__(self):
        return hash(id)


class Node(DbModel):
    short: str


class Group(DbModel):
    short: str
    nodes: Optional[List[Node]] = []

    @classmethod
    async def browse(cls, motor: AsyncIoMotor) -> List[Group]:
        return [cls.parse_obj(item) async for item in motor["groups"].find({})]


class User(DbModel):
    email: EmailStr
    password_hash: str
    username: Optional[str] = None
    groups: Optional[List[Group]] = []

    def authenticate(self, password: str) -> bool:
        return verify_password(password, self.password_hash)

    @classmethod
    async def create(cls, motor: AsyncIoMotor, signup_form: SignupForm) -> User:
        email = signup_form.email
        user = await motor["users"].find_one({"email": email})
        if user is None:
            password_hash = get_password_hash(signup_form.password)
            insert_result = await motor["users"].insert_one({"email": email, "password_hash": password_hash})
            return await motor["users"].find_one({"_id": insert_result.inserted_id})
        else:
            raise ValueError("Email is already in use.")

    @classmethod
    async def read(cls, motor: AsyncIoMotor, **kwargs) -> Optional[User]:
        users = motor["users"]
        user = { key:value for key, value in (await users.find_one(kwargs)).items() if value is not None }
        if user is not None:
            debug(user)
            debug(cls(**user))
            return cls.parse_obj(user)
        else:
            return None

    @classmethod
    async def update(cls, motor: AsyncIoMotor, update_user_model: UpdateUserModel) -> None:
        filter = {"_id": ObjectId(update_user_model.id)}
        update_set = {key: value for key, value in update_user_model.dict(exclude={"id"}, exclude_none=True).items() if
                      not isinstance(value, ForceUnset)}
        update_unset = {key: "" for key, value in update_user_model.dict().items() if isinstance(value, ForceUnset)}
        update = {}
        if update_set:
            update["$set"] = update_set
        if update_unset:
            update["$unset"] = update_unset
        await motor["users"].find_one_and_update(filter, update)
