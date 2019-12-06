from app_factory import make_app
from ponydb import schema
import forge
from fastapi import Form
import ponydb
import ponydb.test_ponydb

db = ponydb.test_db()

ponydb.test_ponydb.populate_test_db(db)

