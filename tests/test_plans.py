import pytest
import json
from bigfastapi.db import database
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bigfastapi.models import plan_models
from bigfastapi.schemas import plan_schemas, users_schemas
from bigfastapi.auth import is_authenticated
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = TestingSessionLocal()


async def override_is_authenticated():
    user_data = {
        "id": "9cd87677378946d88dc7903b6710ae55",
        "first_name": "John",
        "last_name": "Doe",
        "email": "test@gmail.com",
        "password": "hashedpassword",
        "is_active": True,
        "is_verified": True,
        "is_superuser": True,
        "phone_number": "123456789000",
        "organization": "test",
    }
    return users_schemas.User(**user_data)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


client = TestClient(app)


@pytest.fixture(scope="module")
def setUp():
    database.Base.metadata.create_all(engine, tables=[plan_models.Plan.__table__])
    app.dependency_overrides[database.get_db] = override_get_db
    app.dependency_overrides[is_authenticated] = override_is_authenticated

    plan_data_one = {
        "title": "Deluxe",
        "description": "Plan for the elites",
        "price_offers": [
            {"price": 1000.0, "duration": 1, "period": "months"},
            {"price": 9000, "duration": 1, "period": "years"},
        ],
        "available_geographies": json.dumps(["UK", "AS"]),
        "features": json.dumps(["reliable", "trustworthy", "the best"]),
    }

    plan_data_two = {
        "title": "Basic",
        "description": "Plan for the ebrginnrtd",
        "price_offers": [
            {"price": 1000.0, "duration": 1, "period": "months"},
            {"price": 9000, "duration": 1, "period": "years"},
        ],
        "available_geographies": json.dumps(["UK", "AL"]),
        "features": json.dumps(["reliable", "trustworthy", "the best"]),
    }

    plan_one = plan_models.Plan(
        id="9cd87677378946d88dc7903b6710ae44",
        created_by="9cd87677378946d88dc7903b6710ae54",
        **plan_data_one
    )
    plan_two = plan_models.Plan(
        id="9cd87677378946d88dc7903b6710ae45",
        created_by="9cd87677378946d88dc7903b6710ae54",
        **plan_data_two
    )

    db.add(plan_one)
    db.add(plan_two)
    db.commit()
    db.refresh(plan_one)
    db.refresh(plan_two)

    yield plan_schemas.Plan.from_orm(plan_one)

    database.Base.metadata.drop_all(engine, tables=[plan_models.Plan.__table__])


def test_get_all_plans(setUp):
    response = client.get("/plans")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert type(response.json()["data"]) == list
    result = response.json()["data"]
    assert len(result) == 2
    assert type(result[0]["available_geographies"]) == list
    assert type(result[0]["features"]) == list
    assert type(result[0]["price_offers"]) == list


def test_create_plan_success(setUp):
    data = {
        "title": "Economic",
        "description": "Plan for the economical",
        "price_offers":[
            {"price": 1000.0, "duration": 1, "period": "months"},
            {"price": 9000, "duration": 1, "period": "years"},
        ],
        "available_geographies": ["UK", "AL"],
        "features": ["reliable", "trustworthy", "the best"],
    }

    response = client.post("/plans", json=data)
    assert response.status_code == 201
    assert type(response.json()["data"]) == dict
    result = response.json()["data"]
    assert result["title"] == "Economic"
    assert result["description"] == "Plan for the economical"
    assert type(result["available_geographies"]) == list
    assert type(result["features"]) == list
    assert type(result["price_offers"]) == list

def test_create_plan_failure(setUp):
    data = {
        "title": "Basic",
        "description": "Plan for the economical",
        "price_offers": [
            {"price": 1000.0, "duration": 1, "period": "months"},
            {"price": 9000, "duration": 1, "period": "years"},
        ],
        "available_geographies": ["UK", "AL"],
        "features": ["reliable", "trustworthy", "the best"],
    }
    
    response = client.post("/plans", json=data)
    assert response.status_code == 409
    
def test_get_plan_success(setUp):
    response = client.get("/plans/9cd87677378946d88dc7903b6710ae44")
    assert response.status_code == 200
    assert type(response.json()["data"]) == dict
    result = response.json()["data"]
    assert result["title"] == "Deluxe"
    assert result["description"] == "Plan for the elites"
    assert type(result["available_geographies"]) == list
    assert type(result["features"]) == list
    assert type(result["price_offers"]) == list

def test_get_plan_failure(setUp):
    response = client.get("/plans/9cd87677378946d88dc7903b6710ae46")
    assert response.status_code == 404

def test_get_plan_by_geo(setUp):
    response = client.get("/plans/geography/AS")
    assert response.status_code == 200
    assert type(response.json()["data"]) == list
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["title"] == "Deluxe"
        
def test_update_plan_success(setUp):
    data = {
        "title": "Exquisite",
        "description": "Plan for the exquisite",
        "price_offers": [
            {"price": 1000.0, "duration": 1, "period": "months"},
            {"price": 9000, "duration": 1, "period": "years"},
        ],
        "available_geographies": ["UK", "US"],
        "features": ["reliable", "trustworthy", "the best"],
    }
    response = client.put("/plans/9cd87677378946d88dc7903b6710ae44", json=data)
    assert response.status_code == 200
    assert type(response.json()["data"]) == dict
    result = response.json()["data"]
    assert result["title"] == "Exquisite"
    assert result["description"] == "Plan for the exquisite"
    assert type(result["available_geographies"]) == list
    assert result["available_geographies"] == ["UK", "US"]
    assert type(result["features"]) == list
    assert type(result["price_offers"]) == list