from typing import List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel, Field
from pydantic import EmailStr
from pydantic import ValidationError
from pydantic.main import ModelMetaclass

from extensions.mongo import mongo_engine, AsyncIOMotorCollection
from extensions.security import verify_password

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


def get_cn(obj):
    try:
        return obj.collection_name
    except AttributeError:
        try:
            return obj["collection_name"]
        except KeyError:
            raise TypeError(f"Cant' find collection_name in {obj!r}.")


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


class Content(Model):
    collection_name: str = "content"
    short: str
    filetype: str


class Group(Model):
    collection_name: str = "groups"
    short: str
    nodes: List[Model]

    @classmethod
    async def find_by_user(cls, user: "User") -> List["Group"]:
        return await cls.collection.find({"_id": {"$in": [group.id for group in user.groups]}}).to_list(length=MAX_FIND)

    @classmethod
    async def find_by_not_user(cls, user: "User") -> List["Group"]:
        return await cls.collection.find({"_id": {"$nin": [group.id for group in user.groups]}}).to_list(length=MAX_FIND)


class Node(Model):
    collection_name: str = "nodes"
    short: str
    contents: List[Model]

    @classmethod
    async def find_by_groups(cls, groups: list) -> List["Node"]:
        db_models = []
        for item in groups:
            try:
                assert get_cn(item) == "groups"
                db_models.append({"id": get_id(item), "collection_name": get_cn(item)})
            except (AssertionError, TypeError):
                pass
        return [Node.parse_obj(item) for item in await Group.collection.aggregate([
            {"$match": {"_id": {"$in": [model["id"] for model in db_models]}}},
            {"$unwind": {"path": "$nodes"}},
            {"$group": {"_id": None, "all_nodes": {"$push": "$nodes._id"}}},
            {"$lookup": {"from": "nodes", "localField": "all_nodes", "foreignField": "_id", "as": "nodes"}},
            {"$unwind": {"path": "$nodes"}},
            {"$replaceRoot": {"newRoot": "$nodes"}},
            {"$lookup": {"from": "fs.files", "localField": "contents._id", "foreignField": "_id", "as": "contents"}},
            {"$addFields": {"contents": "$contents.metadata"}},
        ]).to_list(length=MAX_FIND)]


class User(Model):
    collection_name: str = "users"
    email: EmailStr
    password_hash: str
    username: str
    groups: List[Model]
    is_admin: bool = False
    is_blocked: bool = False

    def authenticate(self, password: str) -> bool:
        return verify_password(password, self.password_hash)
