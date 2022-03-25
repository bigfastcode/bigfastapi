import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bigfastapi.schemas import notification_schemas, users_schemas
from bigfastapi.models import notification_models
import bigfastapi.db.database as database
from bigfastapi.notification import is_authenticated
from main import app


SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
test_db = TestingSessionLocal()

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


@pytest.fixture
def setUp():
    database.Base.metadata.create_all(bind=engine, tables=[notification_models.Notification.__table__])
    app.dependency_overrides[database.get_db] = override_get_db
    app.dependency_overrides[is_authenticated] = override_is_authenticated

    notification1 = notification_models.Notification(
        id="9cd87677378946d88dc7903b6710ae77", 
        creator="test@gmail.com", 
        content="new comment has been created", 
        reference="comment-9cd87677378946d88dc7903b6710ae67",
        recipient="admin@gmail.com",
    )

    test_db.add(notification1)
    test_db.commit()
    test_db.refresh(notification1)

    yield notification_schemas.Notification.from_orm(notification1)

    database.Base.metadata.drop_all(bind=engine, tables=[notification_models.Notification.__table__])

def test_system_creating_a_notification(setUp):
    response = client.post("/notification", json={"creator": "support@admin.com", "content":"Testing", "reference":"comment-9cd87677378946d88dc7903b6710ae66", "recipient":"hello@test.com"})
    assert response.status_code == 200
    assert response.json().get('creator') == "support@admin.com"
    assert response.json().get('content') == "Testing"

def test_creating_a_notification_authenticated(setUp):
    response = client.post("/notification", json={"creator": "", "content": "Testing Authenticated Creation", "reference": "blog-9cd87677378946d88dc7903b6710ae66", "recipient": "admin@admin.com"})
    assert response.status_code == 200
    assert response.json().get('creator') == "test@gmail.com"
    assert response.json().get('content') == "Testing Authenticated Creation"

def test_get_a_notification(setUp):
    response = client.get("/notification/9cd87677378946d88dc7903b6710ae77")
    assert response.status_code == 200
    assert response.json().get('content') == "new comment has been created"

def test_get_all_notifications(setUp):
    response = client.get("/notifications")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_mark_a_notification_read(setUp):
    response = client.put("/notification/9cd87677378946d88dc7903b6710ae77/read")
    assert response.status_code == 200
    assert response.json().get('has_read') == True
    assert response.json().get('content') == "new comment has been created"

def test_mark_all_notifications_read(setUp):
    response = client.put("/notifications/read")
    assert response.status_code == 200
    assert len(response.json()) == 1
    for n in response.json():
        assert n.get("has_read") == True
    
def test_update_a_notification_content(setUp):
    response = client.put("/notifications/9cd87677378946d88dc7903b6710ae77", json={"content":"Testing!!!", "reference":"", "recipient":""})
    assert response.status_code == 200
    assert response.json().get('content') == "Testing!!!"

def test_update_a_notification_reference(setUp):
    response = client.put("/notifications/9cd87677378946d88dc7903b6710ae77", json={"content":"", "reference":"blog-9cd87677378946d88dc7903b6710ae00", "recipient":""})
    assert response.status_code == 200
    assert response.json().get('reference') == "blog-9cd87677378946d88dc7903b6710ae00"

def test_update_a_notification_recipient(setUp):
    response = client.put("/notifications/9cd87677378946d88dc7903b6710ae77", json={"content":"", "reference":"", "recipient":"admin@test.com"})
    assert response.status_code == 200
    assert response.json().get('recipient') == "admin@test.com"

def test_delete_a_notification(setUp):
    response = client.delete("/notification/9cd87677378946d88dc7903b6710ae77")
    assert response.status_code == 200
    assert response.json().get("message") == "successfully deleted"