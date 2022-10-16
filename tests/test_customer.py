from http import client
from main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bigfastapi.db.database import Base, get_db
from bigfastapi.services.auth_service import is_authenticated
from uuid import uuid4
from bigfastapi.schemas.users_schemas import User


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.drop_all(bind=engine)
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
    user_data =  {
            "id" : uuid4().hex,
            "email" : "test@gmail.com",
            "first_name" : "test",
            "last_name" : "testing",
            "phone_number" : "2340000987866",
            "password":  "hashedpassword",
            "is_active" : True,
            "is_verified" : True,
            "is_superuser" : True,
            "organization" : "spark"
    }

    return User(**user_data)


app.dependency_overrides[is_authenticated] = override_is_authenticated


def test_create_organization():
    response = client.post(
        "/organizations",
        json={
            "mission": "string",
            "vision": "string",
            "name": "spark",
            "values": "string"

        }
    )
    assert response.status_code == 200, response.text
    assert response.json()["name"]== "spark"
    global organization_id
    organization_id = response.json()["id"]

def test_create_customer():
    global organization_id
    response = client.post(
        '/customers',
        json={
            "first_name": "test_name",
            "last_name": "string",
            "organization_id": organization_id,
            "email": "usertest@example.com",
            "phone_number": "string",
            "address": "string",
            "gender": "string",
            "age": 26,
            "postal_code": "string",
            "language": "string",
            "country": "string",
            "city": "string",
            "region": "string"
        }
    )
    assert response.status_code == 200, response.text
    assert response.json()["message"]== "Customer created succesfully"
    assert response.json()["customer"]["organization_id"] == organization_id
    global customer_id
    customer_id = response.json()["customer"]["customer_id"]

def test_get_customers():
    response = client.get(
        '/customers'
    )
    assert response.status_code == 200, response.text
    assert response.json()["items"][0]["first_name"] == "test_name"

def test_get_customers_by_organization():
    organization_id
    response = client.get(
        f'/customers?organization_id={organization_id}'
    )
    assert response.status_code == 200, response.text
    assert response.json()["items"][0]["first_name"] == "test_name"

def test_get_customer():
    global customer_id
    response = client.get(
        f'/customers/{customer_id}'
    )
    assert response.status_code == 200, response.text
    assert response.json()["customer_id"] == customer_id

def test_update_customer():
    global customer_id
    response = client.put(
        f'/customers/{customer_id}',
        json={
            "first_name": "samuel",
            "last_name": "tiangolo",

        }
    )
    assert response.status_code == 200, response.text
    assert response.json()["first_name"] == "samuel"
    assert response.json()["last_name"] == "tiangolo"
    assert response.json()["email"] == "usertest@example.com"

def test_delete_customer():
    global customer_id
    response = client.delete(
        f'/customers/{customer_id}',
    )
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Customer deleted succesfully"






