from .models import *
import os

if os.environ.get("SCALING_SPOON_PRODUCTION"):
    print("Warning: using production database. Do not run tests.")
    db = define_database(provider='sqlite', filename='database.sqlite', create_db=True)
else:
    db = define_database(provider='sqlite', filename=':memory:', create_db=True)

__all__ = ['db', 'db_session']