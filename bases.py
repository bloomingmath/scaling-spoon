import helpers.encryption
from popy import Required, Optional, Set
from pydantic import BaseConfig


class Group:
    short = Required(str, unique=True)
    long = Optional(str)
    public = Required(bool, default=True)
    members = Set("User", reverse="groups")
    nodes = Set("Node", reverse="groups")

    class Config(BaseConfig):
        arbitrary_types_allowed = True

class Node:
    short = Required(str, unique=True)
    long = Optional(str)
    groups = Set("Group", reverse="nodes")

    class Config(BaseConfig):
        arbitrary_types_allowed = True


class User:
    username = Required(str, unique=True)
    email = Required(str, unique=True)
    salt = Required(str)
    hashed = Required(str)
    fullname = Optional(str)
    groups = Set("Group", reverse="members")

    class Config(BaseConfig):
        arbitrary_types_allowed = True

    def create_preparation(self, username: str, email: str, password: str, fullname: str = None):
        salt = helpers.encryption.generate_salt()
        hashed = helpers.encryption.hash_password(salt, password)
        create_info = {"username": username, "email": email, "salt": salt, "hashed": hashed}
        if fullname is not None:
            create_info["fullname"] = fullname
        return create_info

    def get_preparation(self, id: int = None, username: str = None, email: str = None):
        get_info = {}
        if id is not None:
            get_info["id"] = id
        if username is not None:
            get_info["username"] = username
        if email is not None:
            get_info["email"] = email
        return get_info

    def select_preparation(self):
        select_info = {}
        return select_info

    def update_preparation(self, password: str = None, fullname: str = None):
        update_info = {}
        if password is not None:
            salt = self.salt
            hashed = helpers.encryption.hash_password(salt, password)
            update_info["hashed"] = hashed
        if fullname is not None:
            update_info["fullname"] = fullname
        return update_info

    def authenticate(self, password: str):
        return helpers.encryption.verify_password(self.salt, self.hashed, password)
