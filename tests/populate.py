from pony.orm import commit
from pony.orm import db_session

@db_session
def populate(mc):
    User = mc.User
    Group = mc.Group
    u = User.operations.create(dict(username="user", email="user@example.com", password="pass"))
    a = User.operations.create(dict(username="admin", email="admin@example.com", password="pass"))
    ga = Group.operations.create(dict(short="*admin*", public=False))
    g1 = Group.operations.create(dict(short="prima"))
    commit()
    a.groups.add(ga)