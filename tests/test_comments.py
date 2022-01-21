from distutils.errors import CompileError
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from bigfastapi.models import comments_models
from bigfastapi.db import database
from bigfastapi.comments import app as App
from fastapi.testclient import TestClient
from fastapi import FastAPI


@pytest.fixture(scope="function")
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="function")
def tables(engine):
    database.Base.metadata.create_all(engine, tables=[comments_models.Comment.__table__])
    yield
    database.Base.metadata.drop_all(engine, tables=[comments_models.Comment.__table__])


@pytest.fixture
def db_session(engine, tables):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session

    session.close()
    transaction.rollback()
    connection.close()


def get_db(db_session):
    db = db_session()
    try:
        yield db
    finally:
        db.close()


# --------------------------- TESTS ---------------------#
comment_params = {
    "model_name": "posts",
    "rel_id": 1,
    "email": "testmaster@email.com",
    "name": "testmaster",
    "text": "Test Comment Body.",
}


def test_comment_create(db_session):
    new_comment = comments_models.Comment(**comment_params)
    db_session.add(new_comment)
    db_session.commit()
    db_session.refresh(new_comment)
    db_comment = db_session.query(comments_models.Comment).filter(comments_models.Comment.id == 1).first()
    assert db_comment.email == new_comment.email
    assert db_comment.text == new_comment.text
    assert db_comment.name == new_comment.name
    assert db_comment.model_type == new_comment.model_type


def test_comment_threading(db_session):
    p_comment = comments_models.Comment(**comment_params)
    db_session.add(p_comment)
    db_session.commit()
    db_session.refresh(p_comment)

    child_comment = comments_models.Comment(**comment_params)
    child_comment.p_id = p_comment.id
    db_session.add(child_comment)
    db_session.commit()
    db_session.refresh(p_comment)
    db_session.refresh(child_comment)

    fs = p_comment.replies[0]
    assert fs.id == child_comment.id
    assert fs.p_id == p_comment.id


def test_comment_cascade(db_session):
    p_comment = comments_models.Comment(**comment_params)
    db_session.add(p_comment)
    db_session.commit()
    db_session.refresh(p_comment)

    child_comment = comments_models.Comment(**comment_params)
    child_comment.p_id = p_comment.id
    db_session.add(child_comment)
    db_session.commit()

    db_session.delete(p_comment)
    db_session.commit()

    comments_qs = db_session.query(comments_models.Comment).all()
    assert len(comments_qs) == 0


def test_comment_update(db_session):
    update_comment_params = {
        "model_name": "posts",
        "rel_id": 1,
        "email": "tester@yahoo.uk.co",
        "name": "tester",
        "text": "New Content",
    }
    p_comment = comments_models.Comment(**comment_params)
    db_session.add(p_comment)
    db_session.commit()
    db_session.refresh(p_comment)

    child_comment = comments_models.Comment(**comment_params)
    child_comment.p_id = p_comment.id
    db_session.add(child_comment)
    db_session.commit()

    p_comment.email = update_comment_params["email"]
    p_comment.name = update_comment_params["name"]
    p_comment.text = update_comment_params["text"]

    db_session.commit()
    db_session.refresh(p_comment)

    assert p_comment.email == update_comment_params["email"]
    assert child_comment.p_id == p_comment.id


def test_comment_voting(db_session):
    p_comment = comments_models.Comment(**comment_params)
    db_session.add(p_comment)
    db_session.commit()
    db_session.refresh(p_comment)

    p_comment.upvote()
    p_comment.downvote()

    db_session.commit()
    db_session.refresh(p_comment)

    assert p_comment.downvotes == 1
    assert p_comment.upvotes == 1
