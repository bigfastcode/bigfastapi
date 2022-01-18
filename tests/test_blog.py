import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bigfastapi import database as _database, services as _services, models as _models
from bigfastapi.blog import app as Router
import main as _main

app = FastAPI()
app.include_router(Router)


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_is_authenticated():
    user_obj = {
        "id": "123456789",
        "email": "test@admin.com",
        "password": "test1234",
        "firstname": "Test",
        "lastname": "Test",
        "is_active": "true",
        "is_verified": "false",
    }
    return user_obj

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

client = TestClient(app)

blog_data = {"title":"Testing!!!", "content":"Testing Create Blog Endpoint"}
user_data = {"firstname": "John", "lastname": "Doe", "email": "test@admin.com", "password": "123456"} 


@pytest.fixture
def set_up():
    _database.Base.metadata.create_all(engine)
    _main.app.dependency_overrides[_database.get_db] = override_get_db
    _main.app.dependency_overrides[_services.is_authenticated] = override_is_authenticated
    
    yield
    _database.Base.metadata.drop_all(engine)


def test_create_blog(set_up):
    response = client.post("/blog", json=blog_data)
    assert response.status_code == 200
