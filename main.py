import datetime
import random
from uuid import uuid4

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware

from bigfastapi.auth import app as authentication
from bigfastapi.auth_api import app as jwt_services
from bigfastapi.banks import router as banks
from bigfastapi.blog import app as blog
from bigfastapi.products import app as products
from bigfastapi.comments import app as comments
from bigfastapi.contact import app as contact
from bigfastapi.countries import app as countries
from bigfastapi.credit import app as credit
from bigfastapi.customer import app as customer
from bigfastapi.db.database import create_database
from bigfastapi.email import app as email
# Import all the functionality that BFA provides
from bigfastapi.faq import app as faq
from bigfastapi.files import app as files
# from bigfastapi.google_auth import app as social_auth
from bigfastapi.notification import app as notification
from bigfastapi.organization import app as organization
from bigfastapi.pages import app as pages
from bigfastapi.pdfs import app as pdfs
from bigfastapi.plan import app as plan
from bigfastapi.plans import app as plans
from bigfastapi.qrcode import app as qrcode
from bigfastapi.receipts import app as receipts
from bigfastapi.settings import app as settings
from bigfastapi.sms import app as sms
from bigfastapi.subscription import app as sub
from bigfastapi.tutorial import app as tutorial
from bigfastapi.users import app as accounts_router
from bigfastapi.utils import settings as env_var
from bigfastapi.wallet import app as wallet
from bigfastapi.schedule import app as schedule
from bigfastapi.activities_log import app as activitieslog
from bigfastapi.landingpage import app as landingpage

from bigfastapi.api_key import app as api_key
from bigfastapi.failed_imports import app as failedimports
from bigfastapi.import_progress import app as importprogress
from bigfastapi.sales import app as sales

# Create the application
tags_metadata = [
    {
        "name": "blog",
        "description": " BigFast's blog api includes various standard blog api patterns from blog creation to various api querying operations. With this group you can easily get your blog client up and running in no time 📝",
    },
    {
        "name": "auth",
        "description": "BigFast's auth api allows you to manage creation and authentication of users in a seamless manner. You can create new users and authenticate existing users based on specified parameters",
    },
    {
        "name": "countries",
        "description": "BigFast's countries api allows you to get all countries in the world and thier respective states, you can also query for country codes including dial codes and sample phone formats",
    },
    {
        "name": "pages",
        "description": "BigFast's pages api allows you to manage creation, retrieval, updating, and deletion of pages seamlessly. You can create pages with a specified title and content body",
    },
    {
        "name": "notification",
        "description": "BigFast's notifications api  allows you to create notifications and manage the notification flow in your application. You can easily make queries like marking a specific notification as read, marking all notifications as read e.t.c.",
    },
    {
        "name": "activitieslog",
        "description": "BigFast's activity log api allows you to record and manage activity logs for an organization. You can log/record acitvies in an organization and easily retireve them later on."
    },
    {
        "name": "banks",
        "description": "BigFast's bank api allows you to add and manage bank details for an organization. You can also perform operations like validating a bank detail and retrieving a valid bank detail schema for a country of interest"
    },
    {
        "name": "comments",
        "description": "BigFast's comments api allows you easily build a comments architecture for your application. With bigfast's comment api you can manage creation of a comment thread, creation of a comment, replies, updating a comment and deletion of a comment. The comments api also enables upvoting and downvoting a comment"
    },
    {
        "name": "contactsandcontactus",
        "description": "BigFast's contact api allows you to create and manage contact directories while the contact us api allows you to build out a contact us architecture. With the contact us endpoints you can implement sending of a contact us message, retrieval of contact us message and carry out other more specific actions."
    },
    {
        "name": "countries",
        "description": "BigFast's countries api exposes a lot of useful functionalities. You can call and get all countries in the world and their respective states. You can also retreive more specific data using the provided."
    },
    {
        "name": "creditwallet",
        "description": "BigFast's credit api allows you to create and retrieve custom credit rates, you can also add and retrieve credit deails for an organization. It also exposes endpoints you can use to verify payments with payment providers."
    },
    {
        "name": "customers",
        "description": "BigFast's customers api exposes a a group of API routes related to customers. You can seamlessly create, retrieve, update and delete customer details."
    },
    {
        "name": "transactionalemails",
        "description": "BigFast's Transactional Emails api allows you to send emails. We have also made more specific email templates available."
    },
    {
        "name": "file",
        "description": "BigFast's file api allows you upload/store files in our database. When uploading a file, it is stored in a collection which you specify, we call this collection a bucket"
    },
    {
        "name": "organization",
        "description": "BigFast's organization api is very robust, and exposes many essential endpoints you can use to run an organization. You can create and manage an organization, create roles in an organization and mange invites to an organization."
    },
    {
        "name": "plan",
        "description": "BigFast's plan api allows you to create a service plan and retrieve when needed. This is useful for organizations with various service plans for customers"
    },
    {
        "name": "qrcode",
        "description": "BigFast's qr code api provides a unique qr code"
    },
    {
        "name": "settings",
        "description": "BigFast's settings api provides a schema you can use to setup/bootstrap an organization. You can add an organization settings and recall/reference it wherever. This api also allows you you to create custom settings for your application, basically your setting will have a name and a value which can then be retrieved when needed"
    },
    {
        "name": "subscription",
        "description": "BigFast's subscription api allows you create subscription packeges for an organization, which can then be subscribed to by a user"
    },
    {
        "name": "tutorials",
        "description": "BigFast's tutorial is another great api. This api allows you to create and mange tutorials for your application you can specify a category on creation and retrieve later on, based on the category. You can also retrieve a tutorial based on a specified keyword."
    },
    {
        "name": "wallet",
        "description": "BigFast's wallet is another great api. This api allows you to create a wallet for a user in an organization. You can retrieve user wallets based on the organization, the wallet currency e.t.c."
    },
    {
        "name": "user",
        "description": "BigFast's users api allows you and mange user's and user processes in your application."
    },
    {
        "name": "sales",
        "description": "BigFast's sales api exposes a a group of API routes related to sales. You can seamlessly create, retrieve, update and delete sale details."
    },

]

app = FastAPI(openapi_tags=tags_metadata)
app.add_middleware(SessionMiddleware, secret_key=env_var.JWT_SECRET)

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
# app.include_router(social_auth)
app.include_router(accounts_router, tags=["User"])
app.include_router(countries, tags=["Countries"])
app.include_router(faq)
app.include_router(contact)
app.include_router(blog, tags=["Blog"])
app.include_router(products, tags=["Products"])
app.include_router(pages, tags=["Pages"])
app.include_router(plans, tags=['Plans'])
app.include_router(email)
app.include_router(files, tags=["File"])
app.include_router(comments, tags=["Comments"])
app.include_router(sub, tags=["Subscription"])
app.include_router(plan, tags=["Plan"])
app.include_router(tutorial, tags=["Tutorials"])
app.include_router(banks, tags=["Banks"])
app.include_router(countries, tags=["Countries"])
app.include_router(organization, tags=["Organization"])
app.include_router(qrcode, tags=["qrcode"])
app.include_router(settings, tags=["Settings"])
app.include_router(wallet, tags=["Wallet"])
app.include_router(credit, tags=["CreditWallet"])
app.include_router(notification, tags=["Notification"])
app.include_router(pdfs)
app.include_router(jwt_services)
app.include_router(receipts)
app.include_router(customer)
app.include_router(sms)
app.include_router(schedule)
app.include_router(activitieslog)
app.include_router(landingpage)

app.include_router(api_key)
app.include_router(failedimports)
app.include_router(importprogress)
app.include_router(sales)


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
    blog_create_response = client.post("/blog", headers={"Authorization": "Bearer " + user_login_json["access_token"]},
                                       json={
                                           "title": "New Blog Post by " + user_email,
                                           "content": "And this is the body of the blog post by " + user_email, })
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

    # test html convert to pdf
    pdf_response = client.post(app.url_path_for("convertToPdf"), json={
        "htmlString": "new post",
        "pdfName": str(random.random) + "test.pdf"
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
