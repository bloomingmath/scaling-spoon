from logging import info, warning, error
from os import path, getcwd
from typing import Callable, List, Optional

from blinker import signal
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from pickle import dumps, loads
from bson.binary import Binary, USER_DEFINED_SUBTYPE
from bson.codec_options import CodecOptions, TypeDecoder, TypeRegistry


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


def get_extra_collection(db: AsyncIOMotorDatabase, name: str) -> AsyncIOMotorCollection:
    return db.get_collection(name, codec_options=codec_options)


class AsyncIoMotor:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None
    environment: str = "development"

    def init_app(self, app: FastAPI, env: str = "development"):
        async def connect():
            await self.connect_to_mongo()

        async def close():
            await self.close_mongo_connection()

        self.environment = env
        app.add_event_handler("startup", connect)
        app.add_event_handler("shutdown", close)

    async def connect_to_mongo(self):
        from models import User, Group, Node
        info("Connecting to the database...")
        # self.client = AsyncIOMotorClient(
        #     "mongodb+srv://admin:3TrjBbW5fq27YX67@cluster0-txgpn.mongodb.net/?retryWrites=true&w=majority")
        self.client = AsyncIOMotorClient()
        self.database = self.client[f"scaling_spoon_{self.environment}"]
        if self.environment == "development":
            from helpers.security import get_password_hash
            warning("Initialize fresh development database")
            await self.database["nodes"].drop()
            await self.database["groups"].drop()
            await self.database["users"].drop()
            node_list = [Node(short=f"node{i}") for i in range(10)]
            first = Group(short="first", nodes=node_list[0:5])
            second = Group(short="second", nodes=node_list[3:7])
            user = User(**{
                "email": "user@example.com",
                "password_hash": get_password_hash("pass"),
                "groups": [first, second]
            })
            admin = User(**{
                "email": "admin@example.com",
                "password_hash": get_password_hash("pass"),
            })
            await get_extra_collection(self.database, "nodes").insert_many([node.dict() for node in node_list])
            await get_extra_collection(self.database, "groups").insert_many([first.dict(), second.dict()])
            await get_extra_collection(self.database, "users").insert_many([user.dict(), admin.dict()])
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


class SignalsEngine:
    def init_app(self, app: FastAPI):
        """Init app signaling system."""
        assert not hasattr(app, "signals"), "Looks like app already has a signaling system."
        app.signals = {
            "message-flash": signal("message-flash"),
        }
        app.context_store = {}
        signal("message-flash").connect(self.load_flashes)

    @staticmethod
    def load_flashes(sender, **kwargs):
        """This is the 'message-flash' signal receiver. It store (message, category) tuple in app's context_store."""
        message = str(kwargs.get("message", "¿¿¿ ... ???"))
        category = kwargs.get("category", "primary")
        flashes = sender.context_store.get("flashes", [])
        flashes.append((message, category))
        sender.context_store["flashes"] = flashes


mongo_engine = AsyncIoMotor()
render_engine = RenderEngine()
signals_engine = SignalsEngine()


async def get_database() -> AsyncIOMotorDatabase:
    return mongo_engine.database


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


def flash(request, message, category):
    """Signals that a flash message has been dispatched. Somewhere else, the receiver with catch the signal."""
    signal("message-flash").send(request.app, message=message, category=category)


# This function will be a depends in some routes, so request argument must be annotated to be type Request
def get_message_flashes(request: Request):
    """Pop out every message from app.context_store['flashes'] and return them as a list."""
    flashes = request.app.context_store.get("flashes", [])
    request.app.context_store["flashes"] = []
    return flashes
