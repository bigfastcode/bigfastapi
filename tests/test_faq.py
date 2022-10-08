from http import client
import json
from urllib import response
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



def test_create_faq():
    response = client.post(
        '/support/faqs',
        json={"question": "what is our company about?", "answer": "we sell nice products"}
    )
    assert response.status_code == 200, response.text
    assert response.json()["message"]== "Faq created succesfully"



def test_get_faqs():
    response = client.get('/support/faqs')
    assert response.status_code == 200, response.text

def test_create_ticket():
    response = client.post(
        '/support/tickets',
        json={
            "title": "string",
            "issue": "string"
            })
    assert response.status_code == 200, response.text
    assert response.json()["message"]== "Ticket created succesfully"
    global short_id
    short_id = response.json()["ticket"]["short_id"]


def test_get_ticket():
    global short_id
    response = client.get(f'support/ticket/{short_id}')
    assert response.status_code == 200, response.text

def test_get_tickets():
    response = client.get('/support/tickets')
    assert response.status_code == 200, response.text

def test_reply_ticket():
    global short_id
    response = client.post(
        f'/support/tickets/{short_id}/reply',
        json={"reply": "I replied to this ticket"})
    assert response.status_code == 200, response.text
    assert response.json()["message"] ==f"Reply to {short_id}"


def test_close_ticket():
    global short_id
    response = client.put(f'/support/tickets/{short_id}/close')
    assert response.status_code == 200, response.text
    assert response.json()["message"] == f"Ticket with id {short_id} closed"


def test_get_ticket_replies():
    global short_id
    response = client.get(f'/support/tickets/{short_id}/replies')
    assert response.status_code == 200, response.text

def test_get_open_tickets():
    response = client.get(f'/support/tickets/open')
    assert response.status_code == 200, response.text

def test_get_closed_tickets():
    response = client.get(f'/support/tickets/closed')
    assert response.status_code == 200, response.text




