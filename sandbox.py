from pprint import pprint
# import orm
# from orm import db_session
# from orm.crud import create_operation_factory, get_operation_factory, update_operation_factory
# from typing import *
# from pony.orm import Database
#
# db = orm.tdb()
# schemas = orm.schemas
# pprint(schemas.select.content)
# nu = create_operation_factory("User", schemas["UserCreateSchema"])
# gu = get_operation_factory("User", schemas["UserGetSchema"])
# uu = update_operation_factory("User", schemas["UserGetSchema"], schemas["UserUpdateSchema"])
# with db_session:
#     nu(db, {"username": "user", "email": "user@example.com", "password": "pass"})
# with db_session:
#     print("fullname:", gu(db, {"username": "user"}).fullname)
#     uu(db, {"username": "user"}, {"fullname": "John Doe"})
#     print("fullname:", gu(db, {"username": "user"}).fullname)
# with orm.db_session:
#     n = nn(db, {"short": "node0"})
# with orm.db_session:
#     q = db.MultipleChoiceQuestion(long="Quastion 3", options={"key":5}, node=1)
# print(type(q.options))

import simpler_orm.pony_models
from orm import tdb
from pony.orm import Database, db_session
from simpler_orm import pydantic_models
from simpler_orm.base import Model
from simpler_orm import pony_models

db = Database(provider="sqlite", filename=":memory:", create_db=True)
type("Content", (simpler_orm.pony_models.Content, db.Entity), {})
db.generate_mapping(create_tables=True)
with db_session:
    print(db.Content.select()[:])

operations = ("create", "get", "select", "update", "show")

def is_model(x):
    try:
        return issubclass(x, Model) and x is not simpler_orm.base.Model
    except TypeError:
        return False


models = filter(is_model, (getattr(pony_models, model_name) for model_name in dir(pony_models)))
schemas = simpler_orm.pydantic_models.generate_pydantic_schemas(operations, models)
print(schemas.create.content)