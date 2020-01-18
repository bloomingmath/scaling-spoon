from logging import info
from pickle import dumps, loads

from bson.binary import Binary, USER_DEFINED_SUBTYPE
from bson.codec_options import CodecOptions, TypeDecoder, TypeRegistry
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection


def fallback_pickle_encoder(value):
    return Binary(dumps(value), USER_DEFINED_SUBTYPE)


class PickledBinaryDecoder(TypeDecoder):
    bson_type = Binary

    def transform_bson(self, value):
        if value.subtype == USER_DEFINED_SUBTYPE:
            return loads(value)
        return value


codec_options = CodecOptions(type_registry=TypeRegistry(
    [PickledBinaryDecoder()], fallback_encoder=fallback_pickle_encoder))


class AsyncIoMotor:
    app_string: str = None
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None
    environment: str = "development"

    def __getitem__(self, collection_name: str) -> AsyncIOMotorCollection:
        if not hasattr(self, collection_name):
            setattr(self, collection_name, self.database.get_collection(collection_name, codec_options=codec_options))
        return getattr(self, collection_name)

    def init_app(self, app: FastAPI, uri: str = None, env: str = "development") -> None:
        async def connect():
            await self.connect_to_mongo(uri=uri)

        async def close():
            await self.close_mongo_connection()

        self.app_string = ''.join(c if c.isalpha() else "_" for c in list(app.title.lower()))
        self.environment = env
        app.add_event_handler("startup", connect)
        app.add_event_handler("shutdown", close)

    async def connect_to_mongo(self, uri=None):
        info("Connecting to the database... (new-extension)")
        if uri:
            self.client = AsyncIOMotorClient(uri)
        else:
            self.client = AsyncIOMotorClient()
        self.database = self.client[f"{self.app_string}_{self.environment}"]
        if self.environment == "development":
            from .mongo_testing_database import init_testing_database
            await init_testing_database()
        info("Database connection succeeded！")

    async def close_mongo_connection(self):
        info("Closing database connection...")
        self.client.close()
        info("Database connection closed！")


mongo_engine = AsyncIoMotor()


async def get_motor() -> AsyncIoMotor:
    return mongo_engine
