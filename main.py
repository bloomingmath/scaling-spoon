import fastapi
import ponydb
import ponydb.test_ponydb
import routers.admin_api

db = ponydb.test_db()
ponydb.test_ponydb.populate_test_db(db)
app = fastapi.FastAPI()

app.include_router(routers.admin_api.make_router(db), tags=["admin-api"], prefix="/api/admin")
