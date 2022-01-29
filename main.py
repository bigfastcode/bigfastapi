import uvicorn
import datetime
from uuid import uuid4
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
from bigfastapi.subscription import app as sub
from bigfastapi.plan import app as plan
from bigfastapi.db.database import create_database
import random


# Import all the functionality that BFA provides
from bigfastapi.faq import app as faq
from bigfastapi.contact import app as contact
from bigfastapi.blog import app as blog
from bigfastapi.pages import app as pages
from bigfastapi.files import app as files
from bigfastapi.users import app as accounts
from bigfastapi.comments import app as comments
from bigfastapi.countries import app as countries
from bigfastapi.customer import app as customer
from bigfastapi.auth import app as authentication
from bigfastapi.plans import app as plans

from bigfastapi.users import app as accounts_router
from bigfastapi.organization import app as organization_router
from bigfastapi.countries import app as countries
from bigfastapi.faq import app as faq
from bigfastapi.blog import app as blog
from bigfastapi.comments import app as comments
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from bigfastapi import banks
from bigfastapi.pages import app as pages
from bigfastapi.email import app as email
from bigfastapi.organization import app as organization
from bigfastapi.qrcode import app as qrcode
from bigfastapi.settings import app as settings
from bigfastapi.wallet import app as wallet
from bigfastapi.pdfs import app as pdfs
from bigfastapi.receipts import app as receipts
from bigfastapi.notification import app as notification


# Create the application
app = FastAPI()

client = TestClient(app)
create_database()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# routers

app.include_router(authentication, tags=["Auth"])
app.include_router(accounts_router, tags=["User"])
app.include_router(organization_router, tags=["Organization"])
app.include_router(countries, tags=["Countries"])
app.include_router(faq)
app.include_router(contact)
app.include_router(blog, tags=["Blog"])
app.include_router(pages, tags=["Pages"])
app.include_router(plans, tags=['Plans'])
app.include_router(email)
app.include_router(files, tags=["File"])
app.include_router(accounts, tags=["Auth"])
app.include_router(comments, tags=["Comments"])
app.include_router(sub, tags=["Subscription"])
app.include_router(plan, tags=["Plan"])
app.include_router(banks.router, tags=["Banks"])
app.include_router(countries, tags=["Countries"])
app.include_router(organization, tags=["Organization"])
app.include_router(qrcode, tags=["qrcode"])
app.include_router(settings, tags=["Settings"])
app.include_router(wallet, tags=["Wallet"])
app.include_router(notification, tags=["Notification"])
app.include_router(pdfs)
app.include_router(receipts)
app.include_router(customer)

@app.get("/", tags=["Home"])
async def get_root() -> dict:
    return {
        "message": "Welcome to BigFastAPI. This is an example of an API built using BigFastAPI.",
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
    user_email = uuid4().hex + "user@example.com"
    user_create_response = client.post("/users", json={"email": user_email,
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
    user_login_response = client.post(
        "/login", json={"email": user_email, "password": "secret_password", })
    user_login_response = client.post(
        "/login", json={"email": user_email, "password": "secret_password", })
    user_login_json = user_login_response.json()
    print(user_login_json)
    print("Code: " + str(user_login_response.status_code))
    assert user_login_response.status_code == 200

    # Create a blog post
    blog_create_response = client.post("/blog", headers={"Authorization": "Bearer " + user_login_json["access_token"]}, json={
                                       "title": "New Blog Post by " + user_email, "content": "And this is the body of the blog post by " + user_email, })
    blog_create_response = client.post("/blog", headers={"Authorization": "Bearer " + user_login_json["access_token"]},
                                       json={"title": "New Blog Post by " + user_email,
                                             "content": "And this is the body of the blog post by " + user_email, })
    blog_create_json = blog_create_response.json()
    print(blog_create_json)
    print("Response Code: " + str(blog_create_response.status_code))
    assert blog_create_response.status_code == 200

    # Get a list of all blog posts
    blog_list = client.get("/blogs")
    blog_list_json = blog_list.json()
    print(blog_list_json)

    # Test file upload
    txt_file = open("README.md", 'rb').read()

    timestamp_str = datetime.datetime.now().isoformat()
    files = {
        'timestamp': (None, timestamp_str),
        'file': ('readme8.txt', txt_file),
    }

    file_upload_response = client.post("/upload-file/bfafiles/", files=files)
    print(file_upload_response.json())

    #test html convert to pdf 
    pdf_response= client.post(app.url_path_for("convertToPdf"), json={
        "htmlString": "new post",
        "pdfName": str(random.random)+"test.pdf"
    })

    pdf_create_json = pdf_response.json()
    print(pdf_create_json)
    print("Response Code: " + str(pdf_response.status_code))
    assert pdf_response.status_code == 200

    return {
        "message": "Test Results:",
        "create_user_auth_token": create_auth_json["access_token"]["access_token"],
        "login_auth_token": user_login_json["access_token"],
        "blog_list": blog_list_json,
        "pdf": pdf_create_json
    }

if __name__ == "__main__":
    uvicorn.run("main:app", port=7001, reload=True)
