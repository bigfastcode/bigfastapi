import unittest
import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime as _dt
from bigfastapi.comments.internal import fixtures as _fixtures
from bigfastapi.comments.decorators import comment_view_wrapper
import bigfastapi.database as _db 
import bigfastapi.comments.schemas as _schemas


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
        self.actor1 = _fixtures.Actor("Andrew", self.birthday)
        self.session.add_all([self.actor, self.actor1])
        self.session.commit()
        self.session.refresh(self.actor)
        self.session.refresh(self.actor1)

        self.actor_comment = self.actor.Comment(rel_id = self.actor1.id,
                                                name = self.comment_name,
                                                text = self.comment_text,
                                                email = self.comment_email,)
        self.session.add(self.actor_comment)
        self.actor.add_comment(self.actor_comment)
        self.session.commit()
        self.session.refresh(self.actor_comment)

    def tearDown(self):
        _db.Base.metadata.drop_all(self.engine)


    @comment_view_wrapper(action="READ", model_name=_fixtures.Actor)
    @property
    def read_comment_view(*args, **kwargs):
        pass

    @comment_view_wrapper(action="CREATE", model_name=_fixtures.Actor)
    @property
    def create_comment_view(*args, **kwargs):
        pass

    @comment_view_wrapper(action="UPDATE", model_name=_fixtures.Actor)
    @property
    def update_comment_view(*args, **kwargs):
        pass

    @comment_view_wrapper(action="DELETE", model_name=_fixtures.Actor)
    @property
    def delete_comment_view(*args, **kwargs):
        pass

    @comment_view_wrapper(action="VOTE", model_name=_fixtures.Actor)
    @property
    def vote_comment_view(*args, **kwargs):
        pass

    
    @comment_view_wrapper(action="GET", model_name=_fixtures.Actor)
    @property
    def get_comment_view(*args, **kwargs):
        pass
#------------------------------------- TESTS --------------------------------------#
    def test_get_comment_view_decorator(self):
        result = asyncio.run(self.get_comment_view(self.actor_comment.id, db_Session = self.session))
        result_data = result.get("data")
        self.assertEqual(len(result_data), 1)
        fs = result_data[0]
        self.assertEqual(fs, _schemas.Comment.from_orm(self.actor_comment))

    def test_read_comment_view_decorator(self):
        result = asyncio.run(self.read_comment_view(model_name=_fixtures.Actor, object_id=self.actor.id, db_Session=self.session))
        result_data = result.get("data")
        fs = result_data[0]
        self.assertEqual(fs, _schemas.Comment.from_orm(self.actor_comment))

    def test_post_comment_view_decorator(self):
        # Check actor initially doesn't have any comments
        result = asyncio.run(self.read_comment_view(model_name=_fixtures.Actor, object_id=self.actor1.id, db_Session=self.session))
        result_data = result.get("data")
        self.assertEqual(len(result_data), 0)

        # Go ahead to add comment
        new_comment = dict( rel_id = self.actor1.id,
                            name = "testActorName",
                            text = "test content.",
                            email = "test1@tester.com",)
                            
        new_comment = _schemas.CommentCreate.parse_obj(new_comment)

        result = asyncio.run(self.create_comment_view(object_id=self.actor1.id, comment=new_comment, model_name=_fixtures.Actor, db_Session=self.session ))
        result_comment = result.get("data")
        self.assertEqual(result_comment.name, new_comment.name)
        self.assertEqual(result_comment.text, new_comment.text)
        self.assertEqual(result_comment.email, new_comment.email)

        # Check for new comment
        result = asyncio.run(self.read_comment_view(model_name=_fixtures.Actor, object_id=self.actor1.id, db_Session=self.session))
        result_data = result.get("data")
        self.assertEqual(len(result_data), 1)

    def test_update_comment_view_decorator(self):
        new_comment = dict( rel_id = self.actor1.id,
                            name = "testActorName",
                            text = "test content.",
                            email = "test1@tester.com",)
        new_comment = _schemas.CommentUpdate.parse_obj(new_comment)
        
        result = asyncio.run(self.update_comment_view(model_name=_fixtures.Actor, comment_id=self.actor_comment.id, comment=new_comment, db_Session=self.session))
        result_comment = result.get("data")
        self.assertEqual(result_comment.name, new_comment.name)
        self.assertEqual(result_comment.text, new_comment.text)
        self.assertEqual(result_comment.email, new_comment.email)

    def test_delete_comment_view_decorator(self):
        # Delete comment
        result = asyncio.run(self.delete_comment_view(model_name=_fixtures.Actor, comment_id=self.actor_comment.id, db_Session=self.session))
        
        # Check all comments have been deleted
        result = asyncio.run(self.read_comment_view(model_name=_fixtures.Actor, object_id=self.actor_comment.rel_id, db_Session=self.session))
        result_data = result.get("data")
        self.assertEqual(len(result_data), 0)

    def test_vote_comment_view_decorator(self):
        # Test that comment doesn't have any initial votes
        self.assertEqual(self.actor_comment.upvotes, 0)
        self.assertEqual(self.actor_comment.downvotes, 0)

        # Test Upvote
        result = asyncio.run(self.vote_comment_view(model_name=_fixtures.Actor, comment_id=self.actor_comment.id, vote_action="upvote", db_Session=self.session))
        result_data = result.get("data")
        self.assertEqual(result_data.upvotes, 1)

        # Test Downvote
        result = asyncio.run(self.vote_comment_view(model_name=_fixtures.Actor, comment_id=self.actor_comment.id, vote_action="downvote", db_Session=self.session))
        result_data = result.get("data")
        self.assertEqual(result_data.downvotes, 1)
