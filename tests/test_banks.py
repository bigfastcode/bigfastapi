from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bigfastapi.db.database import get_db, Base
from bigfastapi.auth import is_authenticated
from bigfastapi.schemas.users_schemas import User
from main import app
from uuid import uuid4

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


client = TestClient(app)

app.dependency_overrides[get_db] = override_get_db


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
    return User(**user_data)


app.dependency_overrides[is_authenticated] = override_is_authenticated

