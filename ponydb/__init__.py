from .models import *
import functools

# TODO change this for production
std_db = define_database(provider="sqlite", filename=":memory:", create_db=True)
# test_db = define_database(provider="sqlite", filename=":memory:", create_db=True)

# std_db = functools.partial(define_database, provider="sqlite", filename="database.sqlite", create_db=True)
test_db = functools.partial(define_database, provider="sqlite", filename=":memory:", create_db=True)

__all__ = ["db_session", "std_db", "test_db"]