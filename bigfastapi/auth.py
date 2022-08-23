from typing import Union

import fastapi
import sqlalchemy.orm as orm
from decouple import config
from fastapi import APIRouter, BackgroundTasks, Cookie, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from bigfastapi.db.database import get_db
from bigfastapi.services import auth_service
from bigfastapi.utils import settings, utils

from .core.helpers import Helpers
from .models import user_models
from .schemas import auth_schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = settings.JWT_SECRET
ALGORITHM = "HS256"

app = APIRouter(tags=["Auth"])

PYTHON_ENV = config("PYTHON_ENV")
IS_REFRESH_TOKEN_SECURE = True if PYTHON_ENV == "production" else False


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

    if user.email is None and user.phone_number is None:
        raise fastapi.HTTPException(
            status_code=403,
            detail="you must use a either phone_number or email to sign up",
        )
    if user.phone_number and user.phone_country_code is None:
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
    if user.phone_number is None and user.phone_country_code:
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
        if user_email["user"] is not None:
            raise fastapi.HTTPException(
                status_code=403, detail="This email already exist"
            )
        if user.phone_number:
            user_phone = await find_user_phone(
                user.phone_number, user.phone_country_code, db
            )
            if user_phone["user"] is not None:
                raise fastapi.HTTPException(
                    status_code=403, detail="This phone number already exist"
                )
        user_created = await auth_service.create_user(user, db=db)
        access_token = await auth_service.create_access_token(
            data={"user_id": user_created.id}, db=db
        )
        refresh_token = await auth_service.create_refresh_token(
            data={"user_id": user_created.id}, db=db
        )

        background_tasks.add_task(send_slack_notification, user_created)

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="172800",
            secure=IS_REFRESH_TOKEN_SECURE,
            httponly=True,
            samesite="strict",
        )

        return JSONResponse(
            {"data": jsonable_encoder(user_created), "access_token": access_token},
            status_code=201,
        )

    if user.phone_number:
        user_phone = await find_user_phone(
            user.phone_number, user.phone_country_code, db
        )
        if user_phone["user"] is not None:
            raise fastapi.HTTPException(
                status_code=403, detail="Phone_Number already exist"
            )
        user_created = await create_user(user, db=db)
        access_token = await auth_service.create_access_token(
            data={"user_id": user_created.id}, db=db
        )

        refresh_token = await auth_service.create_refresh_token(
            data={"user_id": user_created.id}, db=db
        )

        background_tasks.add_task(send_slack_notification, user_created)

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="172800",
            secure=IS_REFRESH_TOKEN_SECURE,
            httponly=True,
            samesite="strict",
        )

        return JSONResponse(
            {"data": jsonable_encoder(user_created), "access_token": access_token},
            status_code=201,
        )


# ENDPOINT TO CREATE A SUPER ADMIN ACCOUNT
@app.post("/auth/admin-signup", status_code=200)
async def create_admin_user(
    response: Response,
    user: auth_schemas.UserCreate,
    background_tasks: BackgroundTasks,
    db: orm.Session = fastapi.Depends(get_db),
):

    created_user = auth_service.create_user(user, db, True)
    access_token = auth_service.create_access_token(
        data={"user_id": created_user.id}, db=db
    )

    refresh_token = await auth_service.create_refresh_token(
        data={"user_id": created_user["user"].id}, db=db
    )

    background_tasks.add_task(send_slack_notification, created_user)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age="172800",
        secure=IS_REFRESH_TOKEN_SECURE,
        httponly=True,
        samesite="strict",
    )

    return JSONResponse(
        {"data": jsonable_encoder(created_user), "access_token": access_token},
        status_code=201,
    )


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

    if user.email is None and user.phone_number is None:
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
        access_token = await auth_service.create_access_token(
            data={"user_id": userinfo["user"].id}, db=db
        )
        refresh_token = await auth_service.create_refresh_token(
            data={"user_id": userinfo["user"].id}, db=db
        )

        background_tasks.add_task(send_slack_notification, userinfo["response_user"])

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="172800",
            secure=IS_REFRESH_TOKEN_SECURE,
            httponly=True,
            samesite="strict",
        )

        return {"data": userinfo["response_user"], "access_token": access_token}

    if user.phone_number:
        if user.phone_country_code is None:
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
        access_token = await auth_service.create_access_token(
            data={"user_id": userinfo["user"].id}, db=db
        )
        refresh_token = await auth_service.create_refresh_token(
            data={"user_id": userinfo["user"].id}, db=db
        )

        background_tasks.add_task(send_slack_notification, userinfo["response_user"])

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="172800",
            secure=IS_REFRESH_TOKEN_SECURE,
            httponly=True,
            samesite="strict",
        )

        return {"data": userinfo["response_user"], "access_token": access_token}


# change to refresh-access-token
@app.get("/auth/refresh-token", status_code=200)
async def refresh_access_token(
    response: Response,
    refresh_token: Union[str, None] = Cookie(default=None),
    db: orm.Session = fastapi.Depends(get_db),
):

    credentials_exception = fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # check if refresh token is valid

    if refresh_token is None:
        return {"message": "Log in to authenticate user"}

    valid_refresh_token = auth_service.verify_refresh_token(
        refresh_token, credentials_exception, db
    )

    print(refresh_token)
    if valid_refresh_token.email is None:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="172800",
            secure=IS_REFRESH_TOKEN_SECURE,
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

        access_token = await auth_service.create_access_token(
            {"user_id": valid_refresh_token.id}, db
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="172800",
            secure=IS_REFRESH_TOKEN_SECURE,
            httponly=True,
            samesite="strict",
        )

        print("refresh passed", user.id, valid_refresh_token)

    # Access token expires in 15 mins,
    return {"user": user, "access_token": access_token, "expires_in": 900}


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
