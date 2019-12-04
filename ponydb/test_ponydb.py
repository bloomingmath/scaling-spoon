from ponydb import db_session
from ponydb import select
from ponydb import schema
import shutil
import unittest
import helpers.encryption
from app_factory import make_app

app, db = make_app()


class TestDatabase(unittest.TestCase):
    @classmethod
    @db_session
    def setUpClass(cls):
        hpw = helpers.encryption.hash_password('randomsalt', 'pass')
        db.Group.select().delete(bulk=True)
        db.User.select().delete(bulk=True)
        db.Node.select().delete(bulk=True)
        db.MultipleChoiceQuestion.select().delete(bulk=True)
        db.Content.select().delete(bulk=True)

        db.Group(short='admin')
        db.Group(short='teacher')
        for i in range(6):
            db.Group(short='classroom%i' % i)

        db.User(username='admin', email='admin@example.com', salt='randomsalt', hashed=hpw)
        db.Group.get(short='admin').users.add(db.User.get(username='admin'))

        for i in range(6):
            t = db.User(username='teacher%i' % i,
                        email='teacher%i@example.com' % i,
                        salt='randomsalt',
                        hashed=hpw)
            t.groups.add(db.Group.get(short='teacher'))
            t.groups.add(db.Group.get(short='classroom%i' % i))
            for j in range(6):
                u = db.User(username='user%i%i' % (i, j),
                            email='user%i%i@example.com' % (i, j),
                            salt='randomsalt',
                            hashed=hpw)
                u.groups.add(db.Group.get(short='classroom%i' % i))

        for i in range(100):
            short = 'node%02i' % i
            n = db.Node(serial=helpers.encryption.generate_serial(short), short=short)
            for j in range(1, i):
                if i % j == 0:
                    n.antes.add(db.Node.get(short='node%02i' % j))
            for j in range(6):
                qshort = 'question number %i for node%02i' % (j, i)
                qlong = 'Question that expect answer %i' % j
                qserial = helpers.encryption.generate_serial(qshort)
                qoptions = ['it\'s {}'.format(j + k) for k in range(4)]
                db.MultipleChoiceQuestion(serial=qserial, short=qshort, long=qlong, options=qoptions, node=n)

        for filetype in ['md', 'png', 'pdf', 'mp4']:
            n = db.Node.select().first()
            cshort = 'content of type %s' % filetype
            cserial = helpers.encryption.generate_serial(cshort)
            shutil.copy("static/contents/content_example.%s" % filetype, "static/contents/%s.%s" % (cserial, filetype))
            db.Content(serial=cserial, short=cshort, node=n, filetype=filetype)

    @db_session
    def testEntityCreation(self):
        self.assertGreater(db.Group.select().count(), 0)
        self.assertEqual(select(g for g in db.Group if g.short == 'classroom3').count(), 1)
        self.assertEqual(select(g for g in db.Group if g.short == 'notcreated').count(), 0)

    @db_session
    def testRelationshipEstablisment(self):
        self.assertGreater(db.User.get(username='admin').groups.count(), 0)
        self.assertEqual(db.Group.get(short='classroom3').users.count(), 7)


def test_user_create():
    app, db = make_app()
    u = db.User.create(username="user", email="user@example.com", password="pass")
    g = db.Group.create(short="sample")
    n = db.Node.create(short="node01")
    q = db.MultipleChoiceQuestion.create(long="This question expect 5 as answer.",
                                         options_json="[{\"short\": \"5\", \"correct\": true}, {\"short\": \"4\", \"correct\": false}]",
                                         node_serial=str(n.serial))
    c = db.Content.create(short="file01", filetype="png", node_serial=str(n.serial))
    assert isinstance(u, db.User)
    assert isinstance(g, db.Group)
    assert isinstance(n, db.Node)
    assert isinstance(q, db.MultipleChoiceQuestion)
    assert isinstance(c, db.Content)


if __name__ == "__main__":
    unittest.main()
