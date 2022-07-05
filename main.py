from bigfastapi.file_import import app as importprogress
from bigfastapi.api_key import app as api_key
from bigfastapi.landing_page import app as landing_page
from bigfastapi.activity_log import app as activity_log
from bigfastapi.activity_log import app as activitieslog
from bigfastapi.menu import app as menu
import datetime
import random
from uuid import uuid4

import uvicorn
# from bigfastapi import email_marketing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware
from celery import Celery
from decouple import config

from bigfastapi.auth import app as authentication
from bigfastapi.auth_api import app as jwt_services
from bigfastapi.banks import router as banks
from bigfastapi.blog import app as blog
# from bigfastapi.products import app as products
# from bigfastapi.stock import app as stock
# from bigfastapi.product_prices import app as product_prices
from bigfastapi.comments import app as comments
from bigfastapi.contact import app as contact
from bigfastapi.countries import app as countries
from bigfastapi.credit import app as credit
from bigfastapi.db.database import create_database
from bigfastapi.email import app as email
# Import all the functionality that BFA provides
from bigfastapi.faq import app as faq
from bigfastapi.files import app as files
from bigfastapi.google_auth import app as social_auth
from bigfastapi.notification import app as notification
from bigfastapi.organization import app as organization
from bigfastapi.pdfs import app as pdfs
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


# Create the application
tags_metadata = [
    {
        "name": "blog",
        "description": '''BigFast's blog api includes various standard blog api patterns from blog 
        creation to various api querying operations. With this group you can easily get your blog client up and running in no time. You
        can create a blog by specifying it's title and content. We have also created a relationship between blogs and users whereby you can retrieve a blog belonging
        to a specific user.''',
    },
    {
        "name": "auth",
        "description": '''BigFast's authentication api allows you to manage creation and authentication of 
         users in a seamless manner. You can create new users and authenticate existing users based on specified parameters
         We have incorporated a number of the more common details you would typically request from a user and also
         details provided by a third-party such as google id and  google image.''',
    },
    {
        "name": "countries",
        "description": '''BigFast's countries api provides a solution for developers faced with the problem of finding/working with data relating to
        countries around the world. We have sourced very import details about countries and we offer you the ability to
        retrieve all countries in the world along with thier details. You can also query for country codes including dial codes and sample phone formats using this api.''',
    },
    {
        "name": "pages",
        "description": '''BigFast's pages api is used to create pages in your application as the name implies
        Witht he pages  you get to manage creation, retrieval, updating, 
        and deletion of pages seamlessly. You can create pages with a specified title and content body. Each page is
        unique and includes timestamps for reference''',
    },
    {
        "name": "notification",
        "description": '''Using and managing a notification feature is key to facilitating user interactions in
         an application. BigFast's notifications api  saves you from the stress of building a this feature from scratch. You can import
         the notification api into your project and build on top of it. The api offers also offers support for
         marking a specific notification as read, marking all notifications as read e.t.c.''',
    },
    {
        "name": "activitieslog",
        "description": '''BigFast's activity log api is useful for organizations/teams that want to track activities in app or
         plug in a third party service. This api allows you to log/record acitvties
         in an organization and easily track or retrieve them later on.'''
    },
    {
        "name": "banks",
        "description": '''BigFast's bank api is very useful for fintech applications or any application that needs
        to collect the financial/bank details of it's users.  The api allows you to add and manage bank details of
        user's in an organization. You can also perform operations like validating a bank detail and
        retrieving a valid bank detail schema for a country of interest'''
    },
    {
        "name": "comments",
        "description": '''BigFast's comments api allows you to build a comments architecture for your application. 
        With bigfast's comments api you can manage creation of a creation of a comment, managment of comment threads, replies, 
        updating a comment and deletion of a comment. The api presents a robust comments and
        also enables upvoting and downvoting a comment'''
    },
    {
        "name": "contacts and contactUs",
        "description": '''This Bigfast api allows managment of contacts and presents a contact us userflow you can
        import into your application. api allows you to create and
         manage contact directories while the contact us api allows you to build out a
          contact us workflow. With the contact us endpoints you can implement sending of a
           contact us message, retrieval of contact us message and carry out other more specific actions.'''

    },
    {
        "name": "countries",
        "description": '''BigFast's countries api exposes a lot of useful functionalities.
         You can call and get all countries in the world and their respective states. 
          You can also retreive more specific data using the provided. '''
    },
    {
        "name": "creditwallets",
        "description": '''BigFast's credit api allows you to create and retrieve custom credit rates, 
         you can also add and retrieve credit deails for an organization. The api also exposes very important
         and useful set of endpoints you can use to verify payments
         with a number of the common third party payment providers used in many financial applications.'''
    },
    {
        "name": "transactionalemails",
        "description": '''BigFast's Transactional Emails api is very robust and allows sending of emails. 
        We have also made more specific email templates available. Each of the api endpoints have been built to include 
        fields that fit it's purpose and templates you can use depending on the feature you are implementing.'''
    },
    {
        "name": "files",
        "description": '''You can manage files in your application with the BigFast file api. This api allows you upload and store files in our database.
         When uploading a file, it is stored in a collection which you specify, we call this collection a bucket. You can then easily retrieve
         these files later on by referencing the bucket name and filename for a specific file'''
    },
    {
        "name": "organization",
        "description": '''BigFast's organization api is very robust and is a key feature in large scale applications
        where you would need to keep track of multiple organizations. Many of Bigfast's api's have a 
        relationship with the organization feature and keep an organzation_id depending on the currently tracked 
        organization. The api exposes many essential endpoints you can use to run an organization.
         You can create and manage an organization, create roles in an organization and mange invites to an organization.'''
    },
    {
        "name": "plans",
        "description": '''BigFast's plan api allows you to create service plans. This is useful for teams and applications that provide
        services to it's users based on their current service plan. With this api you can setup the credit price,  access type and duration 
        of each plan and use later on to configure set of features for users based on thier service plan.
         This is useful for organizations with various service plans for customers'''
    },
    {
        "name": "settings",
        "description": '''BigFast's settings api provides a schema you can use to setup and bootstrap an organization.
         You can add an organization settings and reference it wherever in your application.
          This api also allows you you to create custom settings for your application. Typically, your setting will have a name and a value
           which can then be retrieved when needed.'''
    },
    {
        "name": "subscriptions",
        "description": '''BigFast's subscription api allows you create subscription packages. This is useful for applications where users will
        need to subscribe to different plans depending on their needs. This api keeps track of the details of the plan and has a relationship
        with the currently referenced organization.'''
    },
    {
        "name": "tutorials",
        "description": '''BigFast's tutorial is another great api. This api allows you to create and mange tutorials in your application.
        This is useful for educational sites of applications offering an educational/tutorials feature.
         The api is robust and will allow you specify categories on creation and retrieve later on.
         You can also retrieve a tutorial based on a specified keyword.'''
    },
    {
        "name": "wallets",
        "description": '''BigFast's wallet api is another great api. 
        This api allows you to create wallets for users in an organization. The api alows you to create different types of 
        wallets based on their currency codes.
         You can retrieve user wallets by organization, the wallet's currency code e.t.c. You can also retireve all transactions tied
         to a particuar wallet.'''
    },
    {
        "name": "users",
        "description": '''BigFast's users api is a very robust and reliable. The users api can be used in any application you will need 
        to keep track of users. The api offers a broad set of features you can import and use in your application. These features include
         managing users and user related processes like user creation, user invites, password reset, profile update, user token verification
         and many more.'''
    },
    {
        "name": "faq and support",
        "description": '''BigFast's Freqently asked questions(FAQ) and Support api allows you to and set up a faq section in your application. This api allows creation and retireval of faqs.
         We also offer a support ticket workflow which you can incorporate into your application. The support feature enables creation,
          reply and closing of support tickets an application where it has been imported into.'''
    },
    {
        "name": "sms",
        "description": '''BigFast's SMS API allows you to send an sms
         with a body of request containing details of the sms action. '''
    },
    {
        "name": "receipts",
        "description": '''BigFast's Receipt API is another useful api that allows you to create reciepts. The reciepts api is
        useful for applications that provide services and need to generate receipts after a payment for a service or
        transaction has been made. You can also configure sending of reciepts to a recepient's email, and retrieving receipt(s) in an organization. 
        We have also exposed an endpoint that supports downloading of these reciepts'''
    },
]

app = FastAPI(openapi_tags=tags_metadata)
app.add_middleware(SessionMiddleware, secret_key=env_var.JWT_SECRET)
RABBITMQ_USERNAME = config('RABBITMQ_USERNAME')
RABBITMQ_PASSWORD = config('RABBITMQ_PASSWORD')
RABBITMQ_HOST_PORT = config('RABBITMQ_HOST_PORT')

celery = Celery(
    'tasks', broker=f'amqp://{RABBITMQ_USERNAME}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST_PORT}')

celery.conf.imports = [
    ''
]

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
app.include_router(social_auth)
app.include_router(accounts_router, tags=["User"])
app.include_router(countries, tags=["Countries"])
app.include_router(faq)
app.include_router(contact)
app.include_router(blog, tags=["Blog"])

app.include_router(plans, tags=['Plans'])
app.include_router(email)
app.include_router(files, tags=["File"])
app.include_router(menu, tags=["Menu"])
app.include_router(comments, tags=["Comments"])
app.include_router(sub, tags=["Subscription"])
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
app.include_router(sms)
# app.include_router(email_marketing, tags=["Email Marketing"])
app.include_router(activity_log)
app.include_router(api_key)
app.include_router(landing_page)
app.include_router(importprogress)



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
