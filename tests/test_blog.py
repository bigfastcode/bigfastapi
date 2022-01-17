import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bigfastapi import database as _database, main as _main, services as _services, models as _models


app = FastAPI()


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_db = TestingSessionLocal()


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
def setUp(mocker):
    _database.Base.metadata.create_all(engine)
    _main.app.dependency_overrides[_database.get_db] = override_get_db

    # user_obj = _models.User(
    #     id = "123456789",email=user_data["email"], password=user_data["password"],
    #     first_name=user_data["firstname"], last_name=user_data["lastname"],
    #     is_active=True, is_verified = False, phone_number="1234567890", is_superuser=False, organization="asdf"
    # )
    # _db.add(user_obj)
    # _db.commit()
    # _db.refresh(user_obj)

    # _main.app.dependency_overrides[_services.is_authenticated] = _services.get_user_by_id(id="123456789", db=_db)
    mock_is_authenticated = mocker.patch("bigfastapi.services.is_authenticated")
    mock_is_authenticated.return_value = {
        "id": "123456789",
        "email": "test@admin.com",
        "password": "test1234",
        "firstname": "Test",
        "lastname": "Test",
        "is_active": "true",
        "is_verified": "false",
    }

    yield
    
    _database.Base.metadata.drop_all(engine)


def test_create_blog(setUp):
    response = client.post("/blog", json=blog_data)
    assert response.status_code == 200
