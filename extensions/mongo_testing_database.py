from logging import warning

from models import Node, Group, User, Content, DBRef
from extensions.mongo import mongo_engine
from .security import get_password_hash
from bson import ObjectId


async def init_testing_database():
    warning("Initialize fresh development database")
    await Node.collection.drop()
    await Group.collection.drop()
    await User.collection.drop()

    async for data in mongo_engine.fs.find():
        warning(f"Deleting:{data._id}")
        mongo_engine.fs.delete(data._id)
    # Pdf example content
    file_id = ObjectId()
    content_1 = Content(id=file_id, short="An example of pdf file.", filetype="pdf")
    grid_in = mongo_engine.fs.open_upload_stream_with_id(
        file_id,
        "pdfexample.pdf",
        metadata=content_1.dict(by_alias=True))
    with open("static/contents/pdfexample.pdf", "rb") as f:
        await grid_in.write(f.read())
        await grid_in.close()

    # Md example content
    file_id = ObjectId()
    content_2 = Content(id=file_id, short="An example of md file.", filetype="md")
    grid_in = mongo_engine.fs.open_upload_stream_with_id(
        file_id,
        "mdexample.pdf",
        metadata=content_2.dict(by_alias=True))
    with open("static/contents/mdexample.md", "rb") as f:
        await grid_in.write(f.read())
        await grid_in.close()


    inserted_nodes_result = await Node.collection.insert_many([
        {"short": f"node{i}", "contents": [
            DBRef(**content_1.dict(by_alias=True)).dict(by_alias=True),
            DBRef(**content_2.dict(by_alias=True)).dict(by_alias=True),
        ]}
        for i in range(10)
    ])
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
            "is_admin": True,
        },
    ])
