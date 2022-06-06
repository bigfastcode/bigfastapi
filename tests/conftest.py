import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bigfastapi.models import product_models, organization_models
from bigfastapi.schemas import product_schemas, users_schemas
from bigfastapi.db.database import Base, get_db
from main import app
from uuid import uuid4

SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture()
def session():
    print("my session fixture ran")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    print("my client fixture ran")
    def override_get_db():

        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture()
def test_user(client):
    print("my test_user fixture ran")
    user_data = {"first_name":"dean",
                 "last_name":"john",
                 "email": "dean@gmail.com",
                 "password": "password123",
                 "country": "Nigeria",
                 "country_code":"+234",
                 "phone_number":"1234567",
                 "organization":"test"}

    res = client.post('/auth/signup', json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def token(test_user):
    return test_user['access_token']

@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    print(token)
    return client


@pytest.fixture
def test_products(test_user, session):
    products_data = [{
                "name": "product1",
                "description": "this is the first product",
                "price": 150,
                "discount": 5,
                "organization_id": "test",
                "unique_id":"ABC123",
                "quantity":10,
                }, 
          {
                "name": "product2",
                "description": "this is the second product",
                "price": 200,
                "discount": 10,
                "organization_id": "test",
                "unique_id":"ABC124",
                "quantity":11},
     {
                "name": "product3",
                "description": "this is the third product",
                "price": 150,
                "discount": 5,
                "organization_id": "test",
                "unique_id":"ABC125",
                "quantity":20}]

    user_data = test_user['data']

    def create_post_model(product):
        return product_models.Product(id=uuid4().hex, created_by=user_data['id'], **product)

    products_map = map(create_post_model, products_data)
    products = list(products_map)

    session.add_all(products)
    session.commit()

    products = session.query(product_models.Product).all()
    return products


