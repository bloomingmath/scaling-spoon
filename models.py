from __future__ import annotations
from popy import Required, Optional
import helpers.encryption


class Content:
    serial = Required(str)
    short = Required(str)
    long = Optional(str)
    # node = Required("Node")
    filetype = Required(str)

    @classmethod
    def create_preparation(cls, short: str, filetype: str, long: str = None):
        from time import time
        serial = helpers.encryption.generate_serial(str(time()))
        create_info = {"short": short, "filetype": filetype, "serial": serial}
        if long is not None:
            create_info["long"] = long
        return create_info

    @classmethod
    def get_preparation(cls, id: int = None, serial: str = None):
        get_info = {}
        if id is not None:
            get_info["id"] = id
        if serial is not None:
            get_info["serial"] = serial
        return get_info

    @classmethod
    def select_preparation(cls, filetype: str = None):
        select_info = {}
        if filetype is not None:
            select_info["filetype"] = filetype
        return select_info

    @classmethod
    def update_preparation(cls, short: str = None, long: str = None):
        update_info = {}
        if short is not None:
            update_info["short"] = short
        if long is not None:
            update_info["long"] = long
        return update_info

    @classmethod
    def show_preparation(cls, short, serial, long, filetype):
        return None


class Group:
    short = Required(str, unique=True)
    long = Optional(str)

    # nodes = Set("Node")
    # users = Set("User")

    @classmethod
    def create_preparation(cls, short: str, long: str = None):
        create_info = {"short": short}
        if long is not None:
            create_info["long"] = long
        return create_info

    @classmethod
    def get_preparation(cls, id: int = None, short: str = None):
        get_info = {}
        if id is not None:
            get_info["id"] = id
        if short is not None:
            get_info["short"] = short
        return get_info

    @classmethod
    def select_preparation(cls, short: str = None):
        select_info = {}
        if short is not None:
            select_info["short"] = short
        return select_info

    @classmethod
    def update_preparation(cls, short: str = None, long: str = None):
        update_info = {}
        if short is not None:
            update_info["short"] = short
        if long is not None:
            update_info["long"] = long
        return update_info

    @classmethod
    def show_preparation(cls, short, long):
        return None

#
# class Node(Model):
#     id = PrimaryKey(int, auto=True)
#     serial = Required(str, unique=True)
#     short = Required(str)
#     long = Optional(str)
#     antes = Set("Node", reverse="posts")
#     posts = Set("Node", reverse="antes")
#     groups = Set("Group")
#     mcquestions = Set("Question", reverse="node")
#     contents = Set("Content")
#
#     def __str__(self):
#         return self.short
#
#     def __repr__(self):
#         return self.short
#
#     @classmethod
#     @db_session
#     def create(cls, short: str, long: str = "") -> Node:
#         from time import time
#         serial = helpers.encryption.generate_serial(str(time()))
#         return cls(serial=serial, short=short, long=long)
#
#     @classmethod
#     @db_session
#     def read(cls, short: str = None, long: str = None, serial: str = None) -> core.Query:
#         query = cls.select()
#         if short is not None:
#             query = query.filter(lambda node: node.short == short)
#         if long is not None:
#             query = query.filter(lambda node: node.long == long)
#         if serial is not None:
#             query = query.filter(lambda node: node.serial == serial)
#         return query
#
#     @db_session
#     def update(self, short: str = None, long: str = None) -> Node:
#         for attr in ("short", "long"):
#             if locals()[attr] is not None:
#                 setattr(self, attr, locals()[attr])
#         return self
#
# class Question(Model):
#     id = PrimaryKey(int, auto=True)
#     serial = Required(str)
#     short = Optional(str)
#     long = Required(str)
#     options = Required(Json)
#     node = Required("Node")
#
#     @classmethod
#     @db_session
#     def create(cls, long: str, options_json: str, node_serial: str, short: str = "") -> MultipleChoiceQuestion:
#         from time import time
#         from json import loads
#         serial = helpers.encryption.generate_serial(str(time()))
#         options = loads(options_json)
#         node = Node.get(serial=node_serial)
#         return cls(serial=serial, short=short, long=long, options=options, node=node)
#
#     @classmethod
#     @db_session
#     def read(cls, short: str = None, long: str = None, serial: str = None, node_serial: str = None) -> core.Query:
#         query = cls.select()
#         if short is not None:
#             query = query.filter(lambda question: question.short == short)
#         if long is not None:
#             query = query.filter(lambda question: question.long == long)
#         if serial is not None:
#             query = query.filter(lambda question: question.serial == serial)
#         if node_serial is not None:
#             query = query.filter(lambda question: question.node == Node.get(serial=node_serial))
#         return query
#
#     @db_session
#     def update(self, short: str = None, long: str = None, options_json: str = None,
#                node_serial: str = None) -> MultipleChoiceQuestion:
#         for attr in ("short", "long", "options_json", "node_serial"):
#             if locals()[attr] is not None:
#                 setattr(self, attr, locals()[attr])
#         return self
#
# class User(Model):
#     id = PrimaryKey(int, auto=True)
#     username = Required(str, unique=True)
#     email = Required(str, unique=True)
#     salt = Required(str)
#     hashed = Required(str)
#     fullname = Optional(str)
#     groups = Set("Group")
#
#     @classmethod
#     @db_session
#     def create(cls, username: str, email: str, password: str, fullname: str = "") -> User:
#         salt = helpers.encryption.generate_salt()
#         hashed = helpers.encryption.hash_password(salt, password)
#         return cls(username=username, email=email, salt=salt, hashed=hashed, fullname=fullname)
#
#     @classmethod
#     @db_session
#     def read(cls, username: str = None, email: str = None, fullname: str = None) -> core.Query:
#         query = cls.select()
#         if username is not None:
#             query = query.filter(lambda user: user.username == username)
#         if email is not None:
#             query = query.filter(lambda user: user.email == email)
#         if fullname is not None:
#             query = query.filter(lambda user: user.fullname == fullname)
#         return query
#
#     @db_session
#     def update(self, password: str = None, fullname: str = None) -> User:
#         if password is not None:
#             hashed = helpers.encryption.hash_password(self.salt, password)
#             self.hashed = hashed
#         if fullname is not None:
#             self.fullname = fullname
#         return self
