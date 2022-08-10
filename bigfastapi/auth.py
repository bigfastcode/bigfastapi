from typing import Union
from uuid import uuid4

import fastapi
import passlib.hash as hash
import sqlalchemy.orm as orm
from fastapi import APIRouter, BackgroundTasks, Cookie, Response
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from bigfastapi.db.database import get_db

# from authlib.integrations.starlette_client import OAuth, OAuthError
from bigfastapi.services import auth_service
from bigfastapi.utils import settings, utils
from bigfastapi.utils.settings import PYTHON_ENV

from .auth_api import create_access_token, create_refresh_token, verify_refresh_token
from .core.helpers import Helpers
from .models import user_models
from .schemas import auth_schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = settings.JWT_SECRET
ALGORITHM = "HS256"

app = APIRouter(tags=["Auth"])


@app.post("/auth/signup", status_code=201)
async def create_user(
    response: Response,
    user: auth_schemas.UserCreate,
    background_tasks: BackgroundTasks,
    db: orm.Session = fastapi.Depends(get_db),
):

    """intro-->This endpoint allows creation of a new user. To create a new user, you need to send a post request to the /auth/signup endpoint with a body of request containing details of the new user.
    paramDesc-->

        reqBody-->email: This is the email of the new user.
        reqBody-->password: This is the unique password of the new user .
        reqBody-->first_name: This is the first name of the new user.
        reqBody-->last_name: This is the last name of the new user.
        reqBody-->phone_number: This is the phone number of the new user.
        reqBody-->country_code: This is the country code of the new user.
        reqBody-->image: This is an image file of the new user, can be of any format.
        reqBody-->device_id: This is the id of the device used at signup.
        reqBody-->country: This is the country name of the new user.
        reqBody-->state: This is the state name of the new user.
        reqBody-->google_id: This is a unique id of the new user's google account.
        reqBody-->google_image: This is the image of the user's google account.

    returnDesc-->On sucessful request, it returns
        returnBody--> "success".
    """

    if user.email == None and user.phone_number == None:
        raise fastapi.HTTPException(
            status_code=403,
            detail="you must use a either phone_number or email to sign up",
        )
    if user.phone_number and user.phone_country_code == None:
        raise fastapi.HTTPException(
            status_code=403,
            detail="you must add a country code when you add a phone number",
        )
    if user.phone_number and user.phone_country_code:
        check_contry_code = utils.dialcode(user.phone_country_code)
        if check_contry_code is None:
            raise fastapi.HTTPException(
                status_code=403, detail="this country code is invalid"
            )
    if user.phone_number == None and user.phone_country_code:
        raise fastapi.HTTPException(
            status_code=403,
            detail="you must add a phone number when you add a country code",
        )
    # if user.country:
    #     check_country = utils.find_country(user.country)
    #     if check_country is None:
    #         raise fastapi.HTTPException(
    #             status_code=403, detail="this country is invalid")

    if user.email or (user.email and user.phone_number):
        user_email = await find_user_email(user.email, db)
        if user_email["user"] != None:
            raise fastapi.HTTPException(status_code=403, detail="Email already exist")
        if user.phone_number:
            user_phone = await find_user_phone(
                user.phone_number, user.phone_country_code, db
            )
            if user_phone["user"] != None:
                raise fastapi.HTTPException(
                    status_code=403, detail="Phone_Number already exist"
                )
        user_created = await create_user(user, db=db)
        access_token = await create_access_token(
            data={"user_id": user_created.id}, db=db
        )
        background_tasks.add_task(send_slack_notification, user_created)

        if PYTHON_ENV == "production":
            response.set_cookie(
                key="access_token",
                value=access_token,
                max_age="172800",
                secure=True,
                httponly=True,
                samesite=None,
            )
        else:
            response.set_cookie(
                key="access_token", value=access_token, max_age="172800", samesite=None
            )

        return {"data": user_created, "access_token": access_token}

    if user.phone_number:
        user_phone = await find_user_phone(
            user.phone_number, user.phone_country_code, db
        )
        if user_phone["user"] != None:
            raise fastapi.HTTPException(
                status_code=403, detail="Phone_Number already exist"
            )
        user_created = await create_user(user, db=db)
        access_token = await create_access_token(
            data={"user_id": user_created.id}, db=db
        )

        refresh_token = await create_refresh_token(
            data={"user_id": user_created.id}, db=db
        )

        background_tasks.add_task(send_slack_notification, user_created)

        if PYTHON_ENV == "production":
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                max_age="172800",
                secure=True,
                httponly=True,
                samesite="strict",
            )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="172800",
            httponly=True,
            samesite="strict",
        )

        return {"data": user_created, "access_token": access_token}


# ENDPOINT TO CREATE A SUPER ADMIN ACCOUNT
@app.post("/auth/admin-signup", status_code=200)
async def create_user(
    response: Response,
    user: auth_schemas.UserCreate,
    background_tasks: BackgroundTasks,
    db: orm.Session = fastapi.Depends(get_db),
):

    created_user = auth_service.create_user(user, db, True)
    access_token = auth_service.create_access_token(
        data={"user_id": create_user.id}, db=db
    )

    refresh_token = await create_refresh_token(
        data={"user_id": created_user["user"].id}, db=db
    )

    background_tasks.add_task(send_slack_notification, create_user)

    if PYTHON_ENV == "production":
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="172800",
            secure=True,
            httponly=True,
            samesite="strict",
        )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age="172800",
        httponly=True,
        samesite="strict",
    )

    return {"data": create_user, "access_token": access_token}


@app.post("/auth/login", status_code=200)
async def login(
    response: Response,
    user: auth_schemas.UserLogin,
    background_tasks: BackgroundTasks,
    db: orm.Session = fastapi.Depends(get_db),
):
    """intro-->This endpoint allows you to login an existing user, to login a user you need to make a post request to the /auth/login endpoint with a required body of requst as specified below

    paramDesc-->
        param-->auth: /auth/login
        reqBody-->email: This is the email of the existing user.
        reqBody-->phone_number: This is the phone number of the existing user.
        reqBody-->country_code: This is the country code of the existing user.
        reqBody-->password: This is the password of the existing user.

    returnDesc-->On sucessful request, it returns
        returnBody--> "success".
    """

    if user.email == None and user.phone_number == None:
        raise fastapi.HTTPException(
            status_code=403,
            detail="you must use a either phone_number or email to login",
        )
    if user.email:
        userinfo = await find_user_email(user.email, db)
        if userinfo["user"] is None:
            raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")
        veri = userinfo["user"].verify_password(user.password)
        if not veri:
            raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")
        access_token = await create_access_token(
            data={"user_id": userinfo["user"].id}, db=db
        )
        refresh_token = await create_refresh_token(
            data={"user_id": userinfo["user"].id}, db=db
        )

        background_tasks.add_task(send_slack_notification, userinfo["response_user"])

        if PYTHON_ENV == "production":
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                max_age="172800",
                secure=True,
                httponly=True,
                samesite="strict",
            )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="172800",
            httponly=True,
            samesite="strict",
        )

        return {"data": userinfo["response_user"], "access_token": access_token}

    if user.phone_number:
        if user.phone_country_code == None:
            raise fastapi.HTTPException(
                status_code=403,
                detail="you must add country_code when using phone_number to login",
            )
        userinfo = await find_user_phone(user.phone_number, user.phone_country_code, db)
        if userinfo["user"] is None:
            raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")
        veri = userinfo["user"].verify_password(user.password)
        if not veri:
            raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")
        access_token = await create_access_token(
            data={"user_id": userinfo["user"].id}, db=db
        )
        refresh_token = await create_refresh_token(
            data={"user_id": userinfo["user"].id}, db=db
        )

        background_tasks.add_task(send_slack_notification, userinfo["response_user"])

        if PYTHON_ENV == "production":
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                max_age="172800",
                secure=True,
                httponly=True,
                samesite="strict",
            )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="172800",
            httponly=True,
            samesite="strict",
        )

        return {"data": userinfo["response_user"], "access_token": access_token}


@app.get("/auth/refresh-token", status_code=200)
async def refresh_token(
    response: Response,
    refresh_token: Union[str, None] = Cookie(default=None),
    db: orm.Session = fastapi.Depends(get_db),
):

    credentials_exception = fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail=f"Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # check if refresh token is valid

    if refresh_token is None:
        return {"message": "Log in to authenticate user"}

    valid_refresh_token = verify_refresh_token(refresh_token, credentials_exception, db)

    if valid_refresh_token.email is None:
        if PYTHON_ENV == "production":
            response.set_cookie(
                key="refresh_token",
                value=None,
                max_age="172800",
                secure=True,
                httponly=True,
                samesite="strict",
            )
        response.set_cookie(
            key="refresh_token",
            value=None,
            max_age="172800",
            httponly=True,
            samesite="strict",
        )

        print("refresh failed")
    else:
        user = (
            db.query(user_models.User)
            .filter(user_models.User.id == valid_refresh_token.id)
            .first()
        )

        access_token = await create_access_token(
            {"user_id": valid_refresh_token.id}, db
        )

        if PYTHON_ENV == "production":
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                max_age="172800",
                secure=True,
                httponly=True,
                samesite="strict",
            )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="172800",
            httponly=True,
            samesite="strict",
        )

        print("refresh passed", user.id, valid_refresh_token)

    # Access token expires in 15 mins,
    return {"user": user, "access_token": access_token, "expires_in": 900}


async def create_user(
    user: auth_schemas.UserCreate, db: orm.Session, is_su: bool = False
):
    su_status = True if is_su else False

    user_obj = user_models.User(
        id=uuid4().hex,
        email=user.email,
        password_hash=hash.sha256_crypt.hash(user.password),
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        is_active=True,
        is_verified=True,
        is_superuser=su_status,
        phone_country_code=user.phone_country_code,
        is_deleted=False,
        google_id=user.google_id,
        google_image_url=user.google_image_url,
        image_url=user.image_url,
        device_id=user.device_id,
    )

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return auth_schemas.UserCreateOut.from_orm(user_obj)


async def find_user_email(email, db: orm.Session):
    found_user = (
        db.query(user_models.User).filter(user_models.User.email == email).first()
    )
    return {
        "user": found_user,
        "response_user": auth_schemas.UserCreateOut.from_orm(found_user),
    }


async def find_user_phone(phone_number, phone_country_code, db: orm.Session):
    found_user = (
        db.query(user_models.User)
        .filter(
            user_models.User.phone_number == phone_number
            and user_models.User.phone_country_code == phone_country_code
        )
        .first()
    )
    return {
        "user": found_user,
        "response_user": auth_schemas.UserCreateOut.from_orm(found_user),
    }


def send_slack_notification(user):
    message = "New login from " + user.email
    # sends the message to slack
    Helpers.slack_notification("LOG_WEBHOOK_URL", text=message)
