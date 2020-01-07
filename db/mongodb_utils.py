import logging

from motor.motor_asyncio import AsyncIOMotorClient
from .mongodb import mongo


async def connect_to_mongo(env: str="development"):
    logging.info("连接数据库中...")
    mongo.client = AsyncIOMotorClient("mongodb+srv://admin:3TrjBbW5fq27YX67@cluster0-txgpn.mongodb.net/?retryWrites=true&w=majority")
    mongo.database = mongo.client[f"scaling_spoon_{env}"]
    logging.info("连接数据库成功！")


async def close_mongo_connection():
    logging.info("关闭数据库连接...")
    mongo.client.close()
    logging.info("数据库连接关闭！")
