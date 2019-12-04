from pony.orm import *
import helpers.encryption
import typing


def define_entities(db):
    class User(db.Entity):
        id = PrimaryKey(int, auto=True)
        username = Required(str, unique=True)
        email = Required(str, unique=True)
        salt = Required(str)
        hashed = Required(str)
        fullname = Optional(str)
        groups = Set('Group')

        @classmethod
        def create(cls, username: str, email: str, password: str, fullname: str = ""):
            salt = helpers.encryption.generate_salt()
            hashed = helpers.encryption.hash_password(salt, password)
            with db_session:
                return cls(username=username, email=email, salt=salt, hashed=hashed, fullname=fullname)

    class Node(db.Entity):
        id = PrimaryKey(int, auto=True)
        serial = Required(str, unique=True)
        short = Required(str)
        long = Optional(str)
        antes = Set('Node', reverse='posts')
        posts = Set('Node', reverse='antes')
        groups = Set('Group')
        mcquestions = Set('MultipleChoiceQuestion')
        contents = Set('Content')

        def __str__(self):
            return self.short

        def __repr__(self):
            return self.short

        @classmethod
        def create(cls, short: str, long: str = ""):
            from time import time
            serial = helpers.encryption.generate_serial(str(time()))
            with db_session:
                return cls(serial=serial, short=short, long=long)

    class MultipleChoiceQuestion(db.Entity):
        id = PrimaryKey(int, auto=True)
        serial = Required(str)
        short = Optional(str)
        long = Required(str)
        options = Required(Json)
        node = Required(Node)

        @classmethod
        def create(cls, long: str, options_json: str, node_serial: str, short: str = ""):
            from time import time
            from json import loads
            serial = helpers.encryption.generate_serial(str(time()))
            options = loads(options_json)
            with db_session:
                node = Node.get(serial=node_serial)
                return cls(serial=serial, short=short, long=long, options=options, node=node)

    class Group(db.Entity):
        id = PrimaryKey(int, auto=True)
        short = Required(str, unique=True)
        long = Optional(str)
        nodes = Set(Node)
        users = Set(User)

        @classmethod
        def create(cls, short: str, long: str = ""):
            with db_session:
                return cls(short=short, long=long)

    class Content(db.Entity):
        id = PrimaryKey(int, auto=True)
        serial = Required(str)
        short = Required(str)
        long = Optional(str)
        node = Required(Node)
        filetype = Required(str)

        @classmethod
        def create(cls, short: str, filetype: str, node_serial: str, long: str = ""):
            from time import time
            serial = helpers.encryption.generate_serial(str(time()))
            with db_session:
                node = Node.get(serial=node_serial)
                return cls(serial=serial, short=short, long=long, node=node, filetype=filetype)
