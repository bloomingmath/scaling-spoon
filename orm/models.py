from .base import Model, Str, Set, Ref, Json
from helpers.encryption import generate_salt, hash_password
import json


class User(Model):
    username = Str("store!  ?get ?query")
    email = Str("store!  ?get ?query")
    fullname = Str("?store  ?query ?update")
    salt = Str("store")
    hashed = Str("store")
    password = Str(" update?")
    groups = Set("Group", "store")

    @classmethod
    def gnr(cls, username: str, email: str, password: str, fullname: str=None):
        info = {"username": username, "email": email, "salt": generate_salt()}
        info["hashed"] = hash_password(info["salt"], password)
        if fullname is not None:
            info["fullname"] = fullname
        return info


class Group(Model):
    short = Str("store!  get? query?")
    long = Str("store?  get? update?")
    users = Set("User", "store")
    nodes = Set("Node", "store")

    @classmethod
    def gnr(cls, short: str, long: str = None):
        info = {"short": short}
        if long is not None:
            info["long"] = long
        return info


class Node(Model):
    short = Str("store get? query? update?")
    long = Str("store? update?")
    antes = Set("Node", "store", reverse="posts")
    posts = Set("Node", "store", reverse="antes")
    groups = Set("Group", "store")
    questions = Set("MultipleChoiceQuestion", "store")
    contents = Set("Content", "store")

    @classmethod
    def gnr(cls, short: str, long: str = None):
        info = {"short": short}
        if long is not None:
            info["long"] = long
        return info


class MultipleChoiceQuestion(Model):
    short = Str("store? get? query? update?")
    long = Str("store update?")
    options = Json("store update?")
    node = Ref("Node", "store get? query?")

    @classmethod
    def gnr(cls, long: str, options_json: str, node_id: int, short: str = None):
        info = {
            "long": long,
            "options": json.loads(options_json),
            "node": node_id,
        }
        if short is not None:
            info["short"] = short
        return info


class Content(Model):
    serial = Str("store get? query?")
    short = Str("store get? query? update?")
    filetype = Str("store query?")
    long = Str("store? update?")
    node = Ref("Node", "store query?")

    @classmethod
    def gnr(cls, short: str, filetype: str, node_id: str, long: str = None):
        info = {
            "short": short,
            "filetype": filetype,
            "node": node_id,
        }
        if long is not None:
            info["long"] = long
        return info


__all__ = ["User", "Group", "Node", "MultipleChoiceQuestion", "Content"]
