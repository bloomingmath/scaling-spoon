from pymongo.mongo_client import MongoClient
from pprint import pprint

client = MongoClient()
database = client["scaling_spoon_development"]
users = database["users"]
groups = database["groups"]
nodes = database["nodes"]


current_user = users.find_one({"email": "user@example.com"})
pprint(list(groups.aggregate([
    {"$match": {"_id": {"$in": [ g["_id"] for g in current_user["groups"]]}}},
    {"$unwind": {"path": "$nodes"}},
    {"$group": {"_id": None, "all_nodes": {"$push": "$nodes._id"}}},
    {"$lookup": {"from": "nodes", "localField": "all_nodes", "foreignField": "_id", "as": "nodes"}},
    {"$unwind": {"path": "$nodes"}},
    {"$replaceRoot": {"newRoot": "$nodes"}},
    {"$lookup": {"from": "fs.files", "localField": "contents._id", "foreignField": "_id", "as": "contents"}},
    {"$addFields": {"contents": "$contents.metadata"}},
])))
