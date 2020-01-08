from logging import info, warning, error
from os import path, getcwd

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase

from starlette.templating import Jinja2Templates
from typing import Callable, List, Optional


class AsyncIoMotor:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None
    environment: str = "development"

    def init_app(self, app: FastAPI, env: str = "development"):
        async def connect():
            await self.connect_to_mongo()
        async def close():
            await self.close_mongo_connection()
        app.add_event_handler("startup", connect)
        app.add_event_handler("shutdown", close)

    async def connect_to_mongo(self):
        info("Connecting to the database...")
        self.client = AsyncIOMotorClient(
            "mongodb+srv://admin:3TrjBbW5fq27YX67@cluster0-txgpn.mongodb.net/?retryWrites=true&w=majority")
        self.database = self.client[f"scaling_spoon_{self.environment}"]
        info("Database connection succeeded！")

    async def close_mongo_connection(self):
        info("Closing database connection...")
        self.client.close()
        info("Database connection closed！")


class RenderEngine:
    jinja2templates: List[Jinja2Templates] = None

    def init_app(self, app: FastAPI, template_directory: str = "templates",
                 template_directories: Optional[List[str]] = None):
        if template_directories is not None:
            self.jinja2templates = [
                Jinja2Templates(directory=path.join(getcwd(), directory)) for directory in template_directories
            ]
        else:
            self.jinja2templates = [Jinja2Templates(directory=path.join(getcwd(), template_directory)), ]


mongo = AsyncIoMotor()
render_engine = RenderEngine()


async def get_database() -> AsyncIOMotorDatabase:
    return mongo.database


async def get_render() -> Callable:
    def render(*args, **kwargs):
        for j2t in render_engine.jinja2templates:
            try:
                return j2t.TemplateResponse(*args, **kwargs)
            except Exception as exc:
                warning(f"render function {type(exc)}", exc_info=True)
        else:
            error("render function -- No templates engine provided.")

    return render
