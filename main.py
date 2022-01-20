import json
from uuid import uuid4
import uvicorn
from fastapi import FastAPI
from bigfastapi.db.database import create_database
from bigfastapi.users import app as accounts_router
from bigfastapi.organization import app as organization_router
from bigfastapi.countries import app as countries
from bigfastapi.faq import app as faq
from bigfastapi.blog import app as blog
from bigfastapi.comments import app as comments
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient


app = FastAPI()

client = TestClient(app)
create_database()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers=["*"]
)

# routers
app.include_router(accounts_router, tags=["Auth"])
app.include_router(organization_router, tags=["Organization"])
app.include_router(countries, tags=["Countries"])
app.include_router(faq)
app.include_router(blog, tags=["Blog"])
app.include_router(comments, tags=["Comments"])

@app.get("/", tags=["Home"])
async def get_root() -> dict:

    return {
        "message": "Welcome to BigFastAPI. This is an example of an API built using BigFastAPI. Please visit here to view the docs:",
        "url": "http://127.0.0.1:7001/docs",
        "test": "http://127.0.0.1:7001/test"
    }

@app.get("/test", tags=["Test"])
async def run_test() -> dict:

    # This function shows you how to use each of the APIs in a practical way
    print("Testing BigFastAPI")

    # Retrieve all countries in the world
    print("Testing Countries - get all countries")
    response = client.get('/countries')
    # print(response.text)
    assert response.status_code == 200, response.text
    

    # Get the states in a particular country
    response = client.get('/countries/AF/states')
    # print(response.text)
    assert response.status_code == 200, response.text
    

    # Get the phone codes of all countries
    response = client.get('/countries/codes')
    # print(response.text)
    assert response.status_code == 200, response.text
    
    
    # Create a new user
    user_email =  uuid4().hex + "user@example.com"
    user_create_response = client.post("/users", json={ "email": user_email,
                                            "password": "secret_password",
                                            "first_name": "John",
                                            "last_name": "Doe",
                                            "verification_method": "code",
                                            "verification_redirect_url": "https://example.com/verify",
                                            "verification_code_length": 5
                                            })
    create_auth_json = user_create_response.json()
    print("Code: " + str(user_create_response.status_code))
    assert user_create_response.status_code == 201
    
    # Login the user
    user_login_response = client.post("/login", json={ "email": user_email, "password": "secret_password",})
    user_login_json = user_login_response.json()
    print(user_login_json)
    print("Code: " + str(user_login_response.status_code))
    assert user_login_response.status_code == 200

    # Create a blog post
    blog_create_response = client.post("/blog", headers={"Authorization": "Bearer " + user_login_json["access_token"]}, json={ "title": "New Blog Post by " + user_email, "content": "And this is the body of the blog post by " + user_email,})
    blog_create_json = blog_create_response.json()
    print(blog_create_json)
    print("Response Code: " + str(blog_create_response.status_code))
    assert blog_create_response.status_code == 200

    blog_list = client.get("/blogs")
    blog_list_json = blog_list.json()
    print(blog_list_json)

    return {
        "message": "Test Results:",
        "create_user_auth_token" : create_auth_json["access_token"]["access_token"],
        "login_auth_token" : user_login_json["access_token"],
        "blog_list" : blog_list_json
    }


if __name__ == "__main__":
     uvicorn.run("main:app", port=7001, reload=True)
     
