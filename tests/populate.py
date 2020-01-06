from pony.orm import commit
from pony.orm import db_session

@db_session
def populate(mc):
    User = mc.User
    Group = mc.Group
    Node = mc.Node
    u = User.operations.create(dict(username="user", email="user@example.com", password="pass"))
    a = User.operations.create(dict(username="admin", email="admin@example.com", password="pass"))
    ga = Group.operations.create(dict(short="*admin*", public=False))
    g1 = Group.operations.create(dict(short="prima"))
    n1 = Node.operations.create(dict(short="first"))
    n2 = Node.operations.create(dict(short="second"))
    n3 = Node.operations.create(dict(short="third"))
    commit()
    a.groups.add(ga)
    n1.groups.add(g1)
    n2.groups.add(g1)
    n3.groups.add(g1)