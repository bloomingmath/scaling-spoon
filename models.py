from typing import List, Union

from bson import ObjectId
from pydantic import BaseModel, Field
from pydantic import EmailStr
from pydantic.main import ModelMetaclass

from extensions.mongo import mongo_engine, AsyncIOMotorCollection
from extensions.security import verify_password
from pydantic import ValidationError


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
        orm_mode = True

    async def deref(self):
        return await mongo_engine[self.collection_name].find_one({"_id": self.id})

    async def unshallow(self, obj=None, level=1):
        if obj is None:
            obj = self.dict()
        if level == 1:
            return obj
        for name, value in obj.items():
            if isinstance(value, list):
                obj[name] = [

                ]
            try:
                obj[name] = await self.unshallow(obj= await DBRef.parse_obj(value).deref(), level=level - 1)
            except ValidationError:
                try:
                    obj[name] = [ await self.unshallow(obj= await DBRef.parse_obj(item).deref(), level=level - 1) for item in value]
                except (TypeError, ValidationError):
                    pass
        return obj

    # async def unshallow(self, level=1):
    #     _dict = {}
    #     for name, field in self.fields.items():
    #         if name == "id" or name == "collection_name":
    #             _dict[name] = getattr(self, name)
    #         elif level == 1:
    #             _dict[name] = getattr(self, name)
    #         elif level > 1:
    #             if field.type_ == DBRef and not field.is_complex():
    #                 dbref = getattr(self, name)
    #                 _dict[name] = getattr(self, name)
    #             elif field.type_ == DBRef and field.is_complex():
    #                 _dict[name] = [dbref.unshallow(level=level - 1) for dbref in getattr(self, name)]
    #             else:
    #                 _dict[name] = getattr(self, name)
    #         else:
    #             pass


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
    contents: List[DBRef]


class User(DBRef):
    collection_name: str = "users"
    email: EmailStr
    password_hash: str
    username: str
    groups: List[DBRef]
    is_admin: bool = False
    is_blocked: bool = False

    def authenticate(self, password: str) -> bool:
        return verify_password(password, self.password_hash)
