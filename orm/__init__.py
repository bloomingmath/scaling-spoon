from pony.orm import db_session
from pony.orm import Database
from pony.orm import PrimaryKey
from pony.orm import Required
from pony.orm import Optional
from pony.orm import Set
from pony.orm import Json
import functools
import typing
from pprint import pprint
from . import models
from . import pydantic_schemas


def database_factory(**db_params):
    db = Database(**db_params)
    for attr in models.__all__:
        type(attr, (db.Entity,), getattr(models, attr).ormmodk(db))
    db.generate_mapping(create_tables=True)
    return db


schemas = pydantic_schemas.generate_pydantic_schemas()

sdb = functools.partial(database_factory, provider="sqlite", filename="database.sqlite", create_db=True)
tdb = functools.partial(database_factory, provider="sqlite", filename=":memory:", create_db=True)

__all__ = ["db_session", "sdb", "tdb", "schemas"]
