from logging import warning

from models import Node, Group, User
from .mongo import AsyncIoMotor
from .security import get_password_hash


async def init_testing_database(motor: AsyncIoMotor):
    warning("Initialize fresh development database")
    await motor["nodes"].drop()
    await motor["groups"].drop()
    await motor["users"].drop()
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
    await motor["nodes"].insert_many([node.dict() for node in node_list])
    await motor["groups"].insert_many([first.dict(), second.dict()])
    await motor["users"].insert_many([user.dict(), admin.dict()])
