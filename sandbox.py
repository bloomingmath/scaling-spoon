from app_factory import make_app
from ponydb import schema
import forge
from fastapi import Form

app, db = make_app()

u = db.User.create(username="user", email="user@example.com", password="pass")
sign = forge.fsignature(db.User.create)
p = sign[3]
print(p.default == forge.empty)
l = [ forge.kwo(name=par.name, type=par.type, default=Form(... if par.default == forge.empty else par.default)) for par in sign ]
print(l)