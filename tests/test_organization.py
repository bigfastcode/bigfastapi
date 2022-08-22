from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bigfastapi.db.database import Base, get_db
from bigfastapi.schemas.users_schemas import User
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


async def override_is_authenticated():
    user_data = {
        "id": uuid4().hex,
        "email": "test@gmail.com",
        "first_name": "test",
        "last_name": "testing",
        "phone_number": "2340000987866",
        "password": "hashedpassword",
        "is_active": True,
        "is_verified": True,
        "is_superuser": True,
        "organization": "spark",
    }

    return User(**user_data)


client = TestClient(app)

app.dependency_overrides[get_db] = override_get_db


def test_create_organization():
    pass


def test_get_organization():
    pass


def test_get_organization_users():
    organization_id = ""
    response = client.get(f"/organizations/{organization_id}/users")
    assert response.status_code == 200
    assert response.json() == {
        "page": "",
        "size": "",
        "total": "",
        "previous_page": "",
        "next_page": "",
        "items": [],
    }
