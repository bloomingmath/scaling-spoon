from logging import info

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase


class AsyncIoMotor:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None

    def init_app(self, app: FastAPI):
        app.add_event_handler("startup", self.connect_to_mongo)
        app.add_event_handler("shutdown", self.close_mongo_connection)

    @staticmethod
    async def connect_to_mongo(env: str = "development"):
        info("Connecting to the database...")
        mongo.client = AsyncIOMotorClient(
            "mongodb+srv://admin:3TrjBbW5fq27YX67@cluster0-txgpn.mongodb.net/?retryWrites=true&w=majority")
        mongo.database = mongo.client[f"scaling_spoon_{env}"]
        info("Database connection succeeded！")

    @staticmethod
    async def close_mongo_connection():
        info("Closing database connection...")
        mongo.client.close()
        info("Database connection closed！")


mongo = AsyncIoMotor()


async def get_database() -> AsyncIOMotorDatabase:
    return mongo.database
