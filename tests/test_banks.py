import pytest
import json
from bigfastapi.db import database
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bigfastapi.models import bank_models
from bigfastapi.schemas import bank_schemas, users_schemas
from bigfastapi.services.auth_service import is_authenticated
from main import app
from bigfastapi.db.database import Base, get_db
from uuid import uuid4


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
test_db = TestingSessionLocal()

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
        "email": "test@zuri.com",
        "first_name": "Sparrow",
        "last_name": "Jack",
        "phone_number": "+2345669506045",
        "password": "hashedpassword",
        "is_active": True,
        "is_verified": True,
        "is_superuser": True,
        "organization": "marquees"
    }
    return users_schemas.User(**user_data)

client = TestClient(app)


@pytest.fixture(scope="module")
def setUp():
    database.Base.metadata.create_all(engine, tables=[bank_models.BankModels.__table__])
    app.dependency_overrides[database.get_db] = override_get_db
    app.dependency_overrides[is_authenticated] = override_is_authenticated

   