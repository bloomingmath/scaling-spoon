from __future__ import annotations
from .base import Model
from pony.orm import Required, Optional, Set, Json


class Content(Model):
    serial = Required(str)
    short = Required(str)
    long = Optional(str)
    node = Required("Node")
    filetype = Required(str)

    @classmethod
    def create_prep(cls, short: str, filetype: str, node_id: str, long: str = None):
        info = {
            "short": short,
            "filetype": filetype,
            "node": node_id,
        }
        if long is not None:
            info["long"] = long
        return info

class Group(Model):
    short = Required(str, unique=True)
    long = Optional(str)
    nodes = Set("Node")
    users = Set("User")

    @classmethod
    def create_prep(cls, short: str, long: str = None):
        info = {"short": short}
        if long is not None:
            info["long"] = long
        return info

class Node(Model):
    short = Required(str)
    long = Optional(str)
    antes = Set("Node", reverse="posts")
    posts = Set("Node", reverse="antes")
    groups = Set("Group")
    questions = Set("Question")
    contents = Set("Content")

    @classmethod
    def create_prep(cls, short: str, long: str = None):
        info = {"short": short}
        if long is not None:
            info["long"] = long
        return info

class Question(Model):
    serial = Required(str)
    short = Optional(str)
    long = Required(str)
    options = Required(Json)
    node = Required("Node")

    @classmethod
    def create_prep(cls, long: str, options_json: str, node_id: int, short: str = None):
        info = {
            "long": long,
            "options": json.loads(options_json),
            "node": node_id,
        }
        if short is not None:
            info["short"] = short
        return info

class User(Model):
    username = Required(str, unique=True)
    email = Required(str, unique=True)
    salt = Required(str)
    hashed = Required(str)
    fullname = Optional(str)
    groups = Set("Group")

    @classmethod
    def create_prep(cls, username: str, email: str, password: str, fullname: str=None):
        info = {"username": username, "email": email, "salt": generate_salt()}
        info["hashed"] = hash_password(info["salt"], password)
        if fullname is not None:
            info["fullname"] = fullname
        return info
#
# def define_entities(db):
#     class Content(db.Entity):
#         id = PrimaryKey(int, auto=True)
#         serial = Required(str)
#         short = Required(str)
#         long = Optional(str)
#         node = Required("Node")
#         filetype = Required(str)
#
#         @classmethod
#         @db_session
#         def create(cls, short: str, filetype: str, node_serial: str, long: str = "") -> Content:
#             from time import time
#             serial = helpers.encryption.generate_serial(str(time()))
#             node = Node.get(serial=node_serial)
#             return cls(serial=serial, short=short, long=long, node=node, filetype=filetype)
#
#         @classmethod
#         @db_session
#         def read(cls, short: str = None, long: str = None, serial: str = None, node_serial: str = None,
#                  filetype: str = None) -> core.Query:
#             query = cls.select()
#             if short is not None:
#                 query = query.filter(lambda content: content.short == short)
#             if long is not None:
#                 query = query.filter(lambda content: content.long == long)
#             if serial is not None:
#                 query = query.filter(lambda content: content.serial == serial)
#             if node_serial is not None:
#                 query = query.filter(lambda content: content.node == Node.get(serial=node_serial))
#             if filetype is not None:
#                 query = query.filter(lambda content: content.filetype == filetype)
#             return query
#
#         @db_session
#         def update(self, short: str = None, long: str = None, node_serial: str = None, filetype: str = None) -> Content:
#             for attr in ("short", "long", "node_serial", "filetype"):
#                 if locals()[attr] is not None:
#                     setattr(self, attr, locals()[attr])
#             return self
#
#     class Group(db.Entity):
#         id = PrimaryKey(int, auto=True)
#         short = Required(str, unique=True)
#         long = Optional(str)
#         nodes = Set("Node")
#         users = Set("User")
#
#         @classmethod
#         @db_session
#         def create(cls, short: str, long: str = "") -> Group:
#             return cls(short=short, long=long)
#
#         @classmethod
#         @db_session
#         def read(cls, short: str = None, long: str = None) -> core.Query:
#             query = cls.select()
#             if short is not None:
#                 query = query.filter(lambda group: group.short == short)
#             if long is not None:
#                 query = query.filter(lambda group: group.long == long)
#             return query
#
#         @db_session
#         def update(self, short: str = None, long: str = None) -> Group:
#             for attr in ("short", "long"):
#                 if locals()[attr] is not None:
#                     setattr(self, attr, locals()[attr])
#             return self
#
#     class Node(db.Entity):
#         id = PrimaryKey(int, auto=True)
#         serial = Required(str, unique=True)
#         short = Required(str)
#         long = Optional(str)
#         antes = Set("Node", reverse="posts")
#         posts = Set("Node", reverse="antes")
#         groups = Set("Group")
#         mcquestions = Set("MultipleChoiceQuestion")
#         contents = Set("Content")
#
#         def __str__(self):
#             return self.short
#
#         def __repr__(self):
#             return self.short
#
#         @classmethod
#         @db_session
#         def create(cls, short: str, long: str = "") -> Node:
#             from time import time
#             serial = helpers.encryption.generate_serial(str(time()))
#             return cls(serial=serial, short=short, long=long)
#
#         @classmethod
#         @db_session
#         def read(cls, short: str = None, long: str = None, serial: str = None) -> core.Query:
#             query = cls.select()
#             if short is not None:
#                 query = query.filter(lambda node: node.short == short)
#             if long is not None:
#                 query = query.filter(lambda node: node.long == long)
#             if serial is not None:
#                 query = query.filter(lambda node: node.serial == serial)
#             return query
#
#         @db_session
#         def update(self, short: str = None, long: str = None) -> Node:
#             for attr in ("short", "long"):
#                 if locals()[attr] is not None:
#                     setattr(self, attr, locals()[attr])
#             return self
#
#     class MultipleChoiceQuestion(db.Entity):
#         id = PrimaryKey(int, auto=True)
#         serial = Required(str)
#         short = Optional(str)
#         long = Required(str)
#         options = Required(Json)
#         node = Required(Node)
#
#         @classmethod
#         @db_session
#         def create(cls, long: str, options_json: str, node_serial: str, short: str = "") -> MultipleChoiceQuestion:
#             from time import time
#             from json import loads
#             serial = helpers.encryption.generate_serial(str(time()))
#             options = loads(options_json)
#             node = Node.get(serial=node_serial)
#             return cls(serial=serial, short=short, long=long, options=options, node=node)
#
#         @classmethod
#         @db_session
#         def read(cls, short: str = None, long: str = None, serial: str = None, node_serial: str = None) -> core.Query:
#             query = cls.select()
#             if short is not None:
#                 query = query.filter(lambda question: question.short == short)
#             if long is not None:
#                 query = query.filter(lambda question: question.long == long)
#             if serial is not None:
#                 query = query.filter(lambda question: question.serial == serial)
#             if node_serial is not None:
#                 query = query.filter(lambda question: question.node == Node.get(serial=node_serial))
#             return query
#
#         @db_session
#         def update(self, short: str = None, long: str = None, options_json: str = None,
#                    node_serial: str = None) -> MultipleChoiceQuestion:
#             for attr in ("short", "long", "options_json", "node_serial"):
#                 if locals()[attr] is not None:
#                     setattr(self, attr, locals()[attr])
#             return self
#
#     class User(db.Entity):
#         id = PrimaryKey(int, auto=True)
#         username = Required(str, unique=True)
#         email = Required(str, unique=True)
#         salt = Required(str)
#         hashed = Required(str)
#         fullname = Optional(str)
#         groups = Set("Group")
#
#         @classmethod
#         @db_session
#         def create(cls, username: str, email: str, password: str, fullname: str = "") -> User:
#             salt = helpers.encryption.generate_salt()
#             hashed = helpers.encryption.hash_password(salt, password)
#             return cls(username=username, email=email, salt=salt, hashed=hashed, fullname=fullname)
#
#         @classmethod
#         @db_session
#         def read(cls, username: str = None, email: str = None, fullname: str = None) -> core.Query:
#             query = cls.select()
#             if username is not None:
#                 query = query.filter(lambda user: user.username == username)
#             if email is not None:
#                 query = query.filter(lambda user: user.email == email)
#             if fullname is not None:
#                 query = query.filter(lambda user: user.fullname == fullname)
#             return query
#
#         @db_session
#         def update(self, password: str = None, fullname: str = None) -> User:
#             if password is not None:
#                 hashed = helpers.encryption.hash_password(self.salt, password)
#                 self.hashed = hashed
#             if fullname is not None:
#                 self.fullname = fullname
#             return self
