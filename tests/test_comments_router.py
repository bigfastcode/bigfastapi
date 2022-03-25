import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from bigfastapi.models import comments_models
from bigfastapi.schemas import comments_schemas
from bigfastapi.db import database
from bigfastapi.comments import app as Router
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker
import json

SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
database.Base.metadata.create_all(engine, tables=[comments_models.Comment.__table__])

MODEL_NAME = "posts"


def override_get_db():
    connection = engine.connect()
    transaction = connection.begin()
    # bind an individual Session to the connection
    db = Session(bind=connection)
    yield db
    db.rollback()
    connection.close()


comment_params = {
    "model_name": MODEL_NAME,
    "rel_id": "1",
    "email": "testmaster@email.com",
    "name": "testmaster",
    "text": "Test Comment Body.",
}

app = FastAPI()
app.include_router(Router)
app.dependency_overrides[database.get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def cs_db_objects():
    db_session = TestingSessionLocal()

    p_comment = comments_models.Comment(**comment_params)
    db_session.add(p_comment)
    db_session.commit()

    child1 = comments_models.Comment(p_id=p_comment.id, **comment_params)
    child2 = comments_models.Comment(p_id=p_comment.id, **comment_params)
    db_session.add_all([child1, child2])
    db_session.commit()
    db_session.refresh(child1)
    db_session.refresh(child2)

    sub1_child1 = comments_models.Comment(p_id=child1.id, **comment_params)
    sub2_child1 = comments_models.Comment(p_id=child1.id, **comment_params)
    db_session.add_all([sub1_child1, sub2_child1])
    db_session.commit()
    db_session.refresh(p_comment)
    return {
        "p_comment": comments_schemas.Comment.from_orm(p_comment),
        "child1": comments_schemas.Comment.from_orm(child1),
        "child2": comments_schemas.Comment.from_orm(child2),
        "sub1_child1": comments_schemas.Comment.from_orm(sub1_child1),
        "sub2_child1": comments_schemas.Comment.from_orm(sub2_child1),
    }


def test_get_comments_for_model(cs_db_objects):
    cdb_objs = cs_db_objects
    p_comment = cdb_objs["p_comment"]
    response = client.get(f"/comments/{MODEL_NAME}")
    assert response.status_code == 200

    data = response.json()["data"]
    retrieved_comment = [i for i in data if i["id"] == p_comment.id]
    assert len(retrieved_comment) >= 1
    retrieved_comment = retrieved_comment[0]
    assert retrieved_comment.get("time_created") == p_comment.time_created.isoformat()


def test_get_comment_for_object(cs_db_objects):
    get_url = "/comments/{model_name}/{object_id}"
    response = client.get(get_url.format(model_name=MODEL_NAME, object_id=1))
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 1


def test_create_comment_for_object(cs_db_objects):
    create_url = "/comments/{model_name}/{object_id}"
    new_comment = comments_schemas.CommentCreate.parse_obj(comment_params)
    response = client.post(
        create_url.format(model_name=MODEL_NAME, object_id=1),
        data=json.dumps(new_comment.dict()),
    )
    assert response.status_code == 200
    returned_comment = response.json().get("data")
    for data_field in comment_params:
        if data_field == "model_name":
            continue
        assert returned_comment[data_field] == comment_params[data_field]


def test_reply_to_comment(cs_db_objects):
    reply_url = "/comments/{model_name}/{comment_id}/reply"
    new_comment = comments_schemas.CommentCreate.parse_obj(comment_params)
    response = client.post(
        reply_url.format(model_name=MODEL_NAME, comment_id=1),
        data=json.dumps(new_comment.dict()),
    )
    assert response.status_code == 200

    returned_comment = response.json().get("data")
    assert returned_comment["p_id"] == 1


def test_downvote_for_comment(cs_db_objects):
    vote_url = "/comments/{model_name}/{comment_id}/vote"
    response = client.post(
        vote_url.format(model_name=MODEL_NAME, comment_id=1) + "?action=downvote"
    )
    assert response.status_code == 200

    returned_comment = response.json()["data"]
    assert returned_comment["downvotes"] == 1


def test_upvote_for_comments(cs_db_objects):
    vote_url = "/comments/{model_name}/{comment_id}/vote"
    response = client.post(
        vote_url.format(model_name=MODEL_NAME, comment_id=1) + "?action=upvote"
    )
    assert response.status_code == 200

    returned_comment = response.json()["data"]
    assert returned_comment["upvotes"] == 1
