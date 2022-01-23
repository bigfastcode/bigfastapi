from http import client
from bigfastapi.email import send_email_background
from main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bigfastapi.db.database import Base, get_db



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







def test_send_invoice_mail():
    response = client.post(
        '/mail/invoice',
        json={
            "subject": "Invoice from BigFastAPI",
            "recipient": "okechukwusamuel16@gmail.com",
            "title": "Invoice for Ps5",
            "first_name": "Psami",
            "amount": "$1000",
            "due_date": "Today Today",
            "payment_link": "paystack.com",
            "invoice_id": "7976GDDHD573JDJVJ",
            "description": "PlayStation 5 Console"
            }
    )
    
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Invoice Email will be sent in the background"


def test_send_receipt_mail():
    response = client.post(
        '/mail/receipt',
        json={
        "subject": "Receipt from BigFastAPI",
        "recipient": "okechukwusamuel16@gmail.com",
        "title": "Payment for Ps5",
        "first_name": "Samuel",
        "amount": "$600",
        "receipt_id": "HDGY4532WHMMS",
        "description": "PlayStation 5 Console"
    }   
    )
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Receipt Email will be sent in the background"


