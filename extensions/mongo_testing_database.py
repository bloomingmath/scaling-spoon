from logging import warning

from models import Node, Group, User
from .security import get_password_hash


async def init_testing_database():
    warning("Initialize fresh development database")
    await Node.collection.drop()
    await Group.collection.drop()
    await User.collection.drop()
    inserted_nodes_result = await Node.collection.insert_many([{"short": f"node{i}"} for i in range(10)])
    inserted_nodes_refs = [{"_id": _id, "collection_name": "nodes"} for _id in inserted_nodes_result.inserted_ids]
    inserted_groups_result = (await Group.collection.insert_many([
        {"short": "first", "nodes": inserted_nodes_refs[0:5]},
        {"short": "second", "nodes": inserted_nodes_refs[3:7]}
    ]))
    inserted_groups_refs = [{"_id": _id, "collection_name": "groups"} for _id in inserted_groups_result.inserted_ids]
    User.collection.insert_many([
        {
            "email": "user@example.com",
            "password_hash": get_password_hash("pass"),
            "username": "",
            "groups": inserted_groups_refs,
        },
        {
            "email": "admin@example.com",
            "password_hash": get_password_hash("pass"),
            "username": "",
            "groups": [],
        },
    ])
