from typing import List, Optional, Union

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel, Field
from pydantic import EmailStr
from pydantic import ValidationError
from pydantic.main import ModelMetaclass

from extensions.mongo import mongo_engine, AsyncIOMotorCollection
from extensions.security import verify_password
from pprint import pprint

MAX_FIND = 500


def get_id(obj):
    try:
        return ObjectId(obj)
    except (InvalidId, TypeError):
        try:
            return ObjectId(obj.id)
        except (InvalidId, TypeError, AttributeError):
            try:
                return ObjectId(obj["id"])
            except (InvalidId, TypeError, KeyError):
                try:
                    return ObjectId(obj["_id"])
                except (InvalidId, TypeError, KeyError):
                    raise TypeError(f"Can't find id in {obj!r}.")


class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(str(v)):
            return ValueError(f"Not a valid ObjectId: {v}")
        return ObjectId(str(v))


class ObjectsProperty(ModelMetaclass):
    @property
    def collection(cls) -> AsyncIOMotorCollection:
        return mongo_engine[getattr(cls, "__field_defaults__").get("collection_name")]


class Model(BaseModel, metaclass=ObjectsProperty):
    id: ObjectIdStr = Field(..., alias="_id")
    collection_name: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: lambda x: str(x)}
        orm_mode = True

    @classmethod
    async def find_one(cls, filter: dict):
        try:
            return cls.parse_obj(await cls.collection.find_one(filter))
        except ValidationError:
            return None

    @classmethod
    async def find_one_and_set(cls, filter: dict, set: dict):
        await cls.collection.find_one_and_update(
            filter=filter,
            update={"$set": set},
        )

    @classmethod
    async def insert_one(cls, obj: dict):
        await cls.collection.insert_one(obj)

    @classmethod
    async def delete_one(cls, filter: dict):
        await cls.collection.delete_one(filter)


class Content(Model):
    collection_name: str = "contents"
    short: str
    filetype: str


class Group(Model):
    collection_name: str = "groups"
    short: str
    nodes: List[Union["Node", ObjectIdStr]]

    @classmethod
    async def find_by_user(cls, user: "User") -> List["Group"]:
        return await cls.collection.find({"_id": {"$in": user.groups}}).to_list(length=MAX_FIND)

    @classmethod
    async def find_by_not_user(cls, user: "User") -> List["Group"]:
        return await cls.collection.find({"_id": {"$nin": user.groups}}).to_list(length=MAX_FIND)

    @classmethod
    async def find_with_complete_nodes(cls) -> List["Group"]:
        return [Group.parse_obj(item) for item in await Group.collection.aggregate([
            {"$match": {}},
            {"$lookup": {"from": "nodes", "localField": "nodes", "foreignField": "_id", "as": "nodes"}},
        ]).to_list(length=MAX_FIND)]


class Node(Model):
    collection_name: str = "nodes"
    short: str
    contents: List[Union["Content", ObjectIdStr]]

    @classmethod
    async def find_by_groups(cls, groups: list) -> List["Node"]:
        group_ids = [get_id(item) for item in groups]
        return [Node.parse_obj(item) for item in await Group.collection.aggregate([
            {"$match": {"_id": {"$in": group_ids}}},
            {"$unwind": {"path": "$nodes"}},
            {"$group": {"_id": None, "all_nodes": {"$push": "$nodes"}}},
            {"$lookup": {"from": "nodes", "localField": "all_nodes", "foreignField": "_id", "as": "nodes"}},
            {"$unwind": {"path": "$nodes"}},
            {"$replaceRoot": {"newRoot": "$nodes"}},
            {"$lookup": {"from": "fs.files", "localField": "contents", "foreignField": "_id", "as": "contents"}},
            {"$addFields": {"contents": "$contents.metadata"}}
        ]).to_list(length=MAX_FIND)]

    @classmethod
    async def find_with_complete_contents(cls) -> List["Node"]:
        return [Node.parse_obj(item) for item in await Node.collection.aggregate([
            {"$match": {}},
            {"$lookup": {"from": "contents", "localField": "contents", "foreignField": "_id", "as": "contents"}},
        ]).to_list(length=MAX_FIND)]


class User(Model):
    collection_name: str = "users"
    email: EmailStr
    password_hash: str
    username: str
    groups: List[Union["Group", ObjectIdStr]]
    is_admin: bool = False
    is_blocked: bool = False

    def authenticate(self, password: str) -> bool:
        return verify_password(password, self.password_hash)

    @classmethod
    async def find_with_complete_groups(cls) -> List["User"]:
        return [User.parse_obj(item) for item in await User.collection.aggregate([
            {"$match": {}},
            {"$lookup": {"from": "groups", "localField": "groups", "foreignField": "_id", "as": "groups"}},
        ]).to_list(length=MAX_FIND)]
