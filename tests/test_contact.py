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


def test_create_contact():
    response = client.post(
        '/contact',
        json={"address": "67, birrell avenue, Sabo. Yaba", "phone": "2449085765909",
              "map_coordinates": "123.4400.50, 34.342.32.5551"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['contact'].get('phone') == "2449085765909"
    print(data)




def test_get_contact():
    response = client.get('/contact')
    assert response.status_code == 200, response.text


def test_update_contact():
    response = client.put("/contact/f9ca02377ef94b198af509994e93d832",
                          json={"address": " ", "phone": "4346534243654", "map_coordinates": "34.564.7586.765, 345.7687.6554"})
    assert response.status_code == 200
    data = response.json()
    assert data['Uc'].get("phone") == "4346534243654"


def test_get_contact_by_id():
    response = client.get("/contact/f9ca02377ef94b198af509994e93d832")
    assert response.status_code == 200, response.text


def delete_contact():
    response = client.delete("/contact/f9ca02377ef94b198af509994e93d832")
    assert response.status_code == 404


# ============================================CONTACT US============================================#
def test_create_contactUS():
    response = client.post(
        '/contactus',
        json={"name": "onyishi james", "email": "jammy@zuri.com",
              "subject": "Revert", "message": "nice application"})
    print(response)
    assert response.status_code == 200, response.text
    data = response.json()
    print(data)
    assert data['message'] == "message sent successfully"


def test_get_all_contactus():
    response = client.get('/contactus')
    assert response.status_code == 200, response.text



def test_get_contactUS_by_id():
    response = client.get('/contactus/fb2887ad6dca4a868b5a34b6d64e12dd')
    assert response.status_code == 200, response.text


def delete_contactUS():
    response = client.delete('/contactus/fb2887ad6dca4a868b5a34b6d64e12dd')
    assert response.status_code == 404
