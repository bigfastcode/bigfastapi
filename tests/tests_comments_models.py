import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime as _dt
from bigfastapi.models import Comment
import bigfastapi.database as _db 

# Write tests to confirm Backrefs on FK Parent IDs
# Write tests to confirm deleting FK results in deleting Children

class TestModels(unittest.TestCase):

    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = Session()
    email = 'pepe@mail.com'
    password = '1234'
    
    name = "MyTestUser"
    birthday = _dt.date(2019,1,2)

    comment_text = "My test comment..."
    comment_name = "TestCommenter"
    comment_email = "test@testers.com"

    def setUp(self):
        _db.Base.metadata.create_all(self.engine)
        self.actor = _fixtures.Actor(self.name, self.birthday)
        self.session.add(self.actor)
        self.session.commit()
        self.session.refresh(self.actor)

    def tearDown(self):
        _db.Base.metadata.drop_all(self.engine)

    def test_actor_creation(self):
        result = self.session.query(_fixtures.Actor).all()
        self.assertEqual(len(result), 1)
        fs = result[0]
        self.assertEqual(fs.name, self.actor.name)
        self.assertEqual(fs.birthday, self.actor.birthday)

    def test_actor_comment_creation(self):
        c = _fixtures.Actor.Comment(
                rel_id = self.actor.id,
                text = self.comment_text,
                name = self.comment_name,
                email = self.comment_email,
                )
        self.actor.add_comment(c)
        self.session.add(self.actor)
        self.session.refresh(self.actor)
        self.assertEqual(len(self.actor.comments), 1)
        
        c = self.actor.comments[0]
        self.assertEqual(c.text, self.comment_text)
        self.assertEqual(c.name, self.comment_name)