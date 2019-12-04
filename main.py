from app_factory import make_app
import routers.admin_api

app, db = make_app(environment="production")

app.include_router(routers.admin_api.make_router(db), tags=["admin-api"], prefix="/api/admin")
