from .models import *

db = define_database(provider='sqlite', filename=':memory:', create_db=True)
#db = define_database(provider='sqlite', filename='database.sqlite', create_db=True)
test_db = define_database(provider='sqlite', filename=':memory:', create_db=True)

__all__ = ['db', 'db_session', 'select', 'test_db']