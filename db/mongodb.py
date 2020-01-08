from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from .mongodb_utils import close_mongo_connection, connect_to_mongo
from fastapi import FastAPI


class AsyncIoMotor:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None

    def init_app(self, app: FastAPI):
        app.add_event_handler("startup", connect_to_mongo)
        app.add_event_handler("shutdown", close_mongo_connection)
