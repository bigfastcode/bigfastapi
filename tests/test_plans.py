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

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = TestingSessionLocal()

async def override_is_authenticated():
    user_data = {
        "id":"9cd87677378946d88dc7903b6710ae55", 
        "first_name": "John", 
        "last_name": "Doe", 
        "email": "test@gmail.com", 
        "password": "hashedpassword", 
        "is_active": True, 
        "is_verified":True, 
        "is_superuser":True, 
        "phone_number":"123456789000", 
        "organization":"test"
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
    database.Base.metadata.create_all(engine)
    app.dependency_overrides[database.get_db] = override_get_db
    app.dependency_overrides[is_authenticated] = override_is_authenticated
    
    plan_data_one = {
        "title":"Deluxe",
        "description":"Plan for the elites",
        "price_offers":{
            1000: {"length":1, "period":"months"},
             9000: {"length":1, "period":"years"}
             }, 
        "available_geographies":json.dumps(["UK","AL"]),
        "features":json.dumps(["reliable","trustworthy","the best"])
    }
    
    plan_data_two = {
        "title":"Basic",
        "description":"Plan for the ebrginnrtd",
        "price_offers":
            {1000: {"length":1, "period":"months"},
             9000: {"length":1, "period":"years"}},
        "available_geographies":json.dumps(["UK","AL"]),
        "features":json.dumps(["reliable","trustworthy","the best"])
    }
    
    plan_one = plan_models.Plan(id="9cd87677378946d88dc7903b6710ae44", created_by="9cd87677378946d88dc7903b6710ae54", **plan_data_one)
    plan_two = plan_models.Plan(id="9cd87677378946d88dc7903b6710ae45", created_by="9cd87677378946d88dc7903b6710ae54", **plan_data_two)
    
    db.add(plan_one)
    db.add(plan_two)
    db.commit()
    db.refresh(plan_one)
    db.refresh(plan_two)
    
    return plan_schemas.Plan.from_orm(plan_one)

def test_get_all_plans(setUp):
    response = client.get("/plans")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert type(response.json()['data']) == list
    result = response.json()['data']
    assert type(result[0]['available_geographies']) == list
    assert type(result[0]['features']) == list
    assert type(result[0]['price_offers']) == dict
    database.Base.metadata.drop_all(engine)
    # assert response.json() == plan_schemas.Plan.from_orm(plan_models.Plan.query.get("9cd87677378946d88dc7903b6710ae44"))