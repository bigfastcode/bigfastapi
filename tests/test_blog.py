import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bigfastapi import database as _database, services as _services, models as _models, schema as _schemas
from main import app


SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
_db = TestingSessionLocal()

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
    return _schemas.User(**user_data)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

client = TestClient(app)


@pytest.fixture(scope="module")
def setUp():
    _database.Base.metadata.create_all(engine)
    app.dependency_overrides[_database.get_db] = override_get_db
    app.dependency_overrides[_services.is_authenticated] = override_is_authenticated

    blog_data1 = {"title":"First Test Data", "content":"Testing Blog Endpoint"}
    blog_data2 = {"title":"Second Test Data", "content":"Testing Blog Update Endpoint"}
    blog_data3 = {"title":"Third Test Data", "content":"Testing Update Endpoint"}
    
    blog1 = _models.Blog(id="9cd87677378946d88dc7903b6710ae44", creator="9cd87677378946d88dc7903b6710ae54", **blog_data1)
    blog2 = _models.Blog(id="9cd87677378946d88dc7903b6710ae45", creator="9cd87677378946d88dc7903b6710ae55", **blog_data2)
    blog3 = _models.Blog(id="9cd87677378946d88dc7903b6710ae46", creator="9cd87677378946d88dc7903b6710ae55", **blog_data3)
    _db.add(blog1)
    _db.add(blog2)
    _db.add(blog3)
    _db.commit()
    _db.refresh(blog1)
    _db.refresh(blog2)
    _db.refresh(blog3)

    yield _schemas.Blog.from_orm(blog1)

    _database.Base.metadata.drop_all(engine)


def test_create_blog(setUp):
    response = client.post("/blog", json={"title":"Testing Create Endpoint!!!", "content":"Testing Create Blog Endpoint"})
    assert response.status_code == 200
    assert response.json().get("title") == "Testing Create Endpoint!!!"

def test_create_blog_with_existing_title(setUp):
    response = client.post("/blog", json={"title":"First Test Data", "content":"Testing Create Blog Endpoint"})
    assert response.status_code == 400
    assert response.json().get("detail") == "Blog title already exists"

def test_get_all_blogs(setUp):
    response = client.get("/blogs")
    assert response.status_code == 200
    assert len(response.json()) == 4

def test_get_blog(setUp):
    response = client.get("/blog/9cd87677378946d88dc7903b6710ae44")
    response.status_code = 200
    assert response.json().get("title") == "First Test Data"
    assert response.json().get("content") == "Testing Blog Endpoint"

def test_get_user_blogs(setUp):
    response = client.get("/blogs/9cd87677378946d88dc7903b6710ae55")
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_update_blog(setUp):
    response = client.put("/blog/9cd87677378946d88dc7903b6710ae45", json={"title": "","content": "Testing Update Blog Endpoint!!!"})
    assert response.status_code == 200
    assert response.json().get("title") == "Second Test Data"
    assert response.json().get("content") == "Testing Update Blog Endpoint!!!"

def test_update_blog_title_with_existing_title(setUp):
    response = client.put("/blog/9cd87677378946d88dc7903b6710ae45", json={"title": "Second Test Data", "content": ""})
    assert response.status_code == 400
    assert response.json().get("detail") == "Blog title already in use"

def test_update_blog_that_was_not_created_by_user(setUp):
    response = client.put("/blog/9cd87677378946d88dc7903b6710ae44", json={"title": "Second Test Data", "content": "Testing Update Blog Endpoint"})
    assert response.status_code == 404

def test_delete_blog(setUp):
    response = client.delete("/blog/9cd87677378946d88dc7903b6710ae46")
    assert response.status_code == 200
    assert response.json().get("message") == "successfully deleted"

def test_delete_blog_that_was_not_created_by_user(setUp):
    response = client.delete("/blog/9cd87677378946d88dc7903b6710ae44")
    assert response.status_code == 404