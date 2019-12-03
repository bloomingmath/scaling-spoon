from pony.orm import *

def define_entities(db):
    class User(db.Entity):
        id = PrimaryKey(int, auto=True)
        username = Required(str, unique=True)
        email = Required(str, unique=True)
        salt = Required(str)
        hashed = Required(str)
        fullname = Optional(str)
        groups = Set('Group')


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


    class MultipleChoiceQuestion(db.Entity):
        id = PrimaryKey(int, auto=True)
        serial = Required(str)
        short = Optional(str)
        long = Required(str)
        options = Required(Json)
        node = Required(Node)


    class Group(db.Entity):
        id = PrimaryKey(int, auto=True)
        short = Required(str, unique=True)
        long = Optional(str)
        nodes = Set(Node)
        users = Set(User)


    class Content(db.Entity):
        id = PrimaryKey(int, auto=True)
        serial = Required(str)
        short = Required(str)
        long = Optional(str)
        node = Required(Node)
        filetype = Required(str)

def define_database(**db_params):
    db = Database(**db_params)
    define_entities(db)
    db.generate_mapping(create_tables=True)
    return db