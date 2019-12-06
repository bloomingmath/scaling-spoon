from ponydb import db_session
import ponydb
import unittest

db = ponydb.test_db()

@db_session
def populate_test_db(db: type(ponydb.schema)) -> None:
    import json
    db.Group.create(short="@ADMIN")
    db.Group.create(short="@TEACHER")
    for i in range(6):
        db.Group.create(short=f"CLASSROOM{i}")
    db.User.create(username="admin", email="admin@example.com", password="pass")

    db.Group.get(short='@ADMIN').users.add(db.User.get(username='admin'))

    for i in range(6):
        t = db.User.create(username=f"teacher{i}", email=f"teacher{i}@example.com", password="pass")
        t.groups.add(db.Group.get(short="@TEACHER"))
        t.groups.add(db.Group.get(short=f"CLASSROOM{i}"))
        for j in range(6):
            u = db.User.create(username=f"user{i}{j}", email=f"user{i}{j}@example.com", password="pass")
            u.groups.add(db.Group.get(short=f"CLASSROOM{i}"))

    for i in range(10):
        short = 'node%02i' % i
        n = db.Node.create(short=f"node{i:02}")
        for j in range(1, i):
            if i % j == 0:
                n.antes.add(db.Node.get(short=f"node{j:02}"))
        for j in range(6):
            db.MultipleChoiceQuestion.create(long=f"Question that expect answer {j}.", options_json=json.dumps(
                [{"short": f"It's {j + k}", "correct": bool(k == 0)} for k in range(4)]), node_serial=n.serial)
    # This tests dumps lots of garbage in the content directory
    # for filetype in ['md', 'png', 'pdf', 'mp4']:
    #     n = db.Node.select().first()
    #     cshort = f"Content of type {filetype}"
    #     c = db.Content.create(short=cshort, node_serial=n.serial, filetype=filetype)
    #     shutil.copy(f"static/examples/content_example.{filetype}", f"static/contents/{c.serial}.{filetype}")


class TestDatabase(unittest.TestCase):
    @classmethod
    @db_session
    def setUpClass(cls):
        populate_test_db(db)

    @db_session
    def testEntityCreation(self):
        self.assertGreater(db.Group.select().count(), 0)
        assert db.Group.read(short="CLASSROOM3").count() == 1
        assert db.Group.read(short="NOTCREATED").count() == 0

    @db_session
    def testRelationshipEstablisment(self):
        assert db.User.get(username="admin").groups.count() == 1
        assert db.Group.get(short="CLASSROOM3").users.count() == 7


if __name__ == "__main__":
    unittest.main()
