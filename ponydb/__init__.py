from .models import define_entities
from pony.orm import db_session
from pony.orm import Database
from pony.orm import select
import functools

def define_database(**db_params):
    db = Database(**db_params)
    define_entities(db)
    db.generate_mapping(create_tables=True)
    return db

# TODO change this for production
# std_db = define_database(provider="sqlite", filename="database.sqlite", create_db=True)
# test_db = define_database(provider="sqlite", filename=":memory:", create_db=True)

std_db = functools.partial(define_database, provider="sqlite", filename="database.sqlite", create_db=True)
test_db = functools.partial(define_database, provider="sqlite", filename=":memory:", create_db=True)

schema = Database()
models.define_entities(schema)

__all__ = ["db_session", "std_db", "test_db", "schema", "select"]

#
# __all__ = ["db_session", "std_db", "test_db", "Database"]
