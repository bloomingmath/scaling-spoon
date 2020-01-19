from __future__ import annotations

from typing import List, Union

from bson import ObjectId
from pydantic import BaseModel, Field
from pydantic import EmailStr
from pydantic.main import ModelMetaclass

from extensions.mongo import mongo_engine, AsyncIOMotorCollection
from extensions.security import verify_password


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


class DBRef(BaseModel, metaclass=ObjectsProperty):
    id: ObjectIdStr = Field(..., alias="_id")
    collection_name: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: lambda x: str(x)}


class Content(DBRef):
    collection_name: str = "content"
    short: str
    filetype: str


class Group(DBRef):
    collection_name: str = "groups"
    short: str
    nodes: List[DBRef]


class Node(DBRef):
    collection_name: str = "nodes"
    short: str
    contents: List[Union[Content, DBRef]]


class User(DBRef):
    collection_name: str = "users"
    email: EmailStr
    password_hash: str
    username: str
    groups: List[DBRef]

    def authenticate(self, password: str) -> bool:
        return verify_password(password, self.password_hash)
