from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase


class AsyncIoMotor:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None


mongo = AsyncIoMotor()


async def get_database() -> AsyncIOMotorDatabase:
    return mongo.database


async def get_client() -> AsyncIOMotorDatabase:
    return mongo.client
