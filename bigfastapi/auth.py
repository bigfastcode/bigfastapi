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
from bigfastapi.utils import settings

from .models import auth_models, user_models
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

    new_user = await auth_service.create_user(user=user, db=db)

    if new_user is not None:
        access_token = await auth_service.create_access_token(
            data={"user_id": new_user.id}, db=db
        )

        refresh_token = await auth_service.create_refresh_token(
            data={"user_id": new_user.id}, db=db
        )

        background_tasks.add_task(
            auth_service.send_slack_notification_for_auth, new_user, "signup"
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="172800",
            secure=IS_REFRESH_TOKEN_SECURE,
            httponly=True,
            samesite="strict",
        )
        
        response_data = {
            "data": jsonable_encoder(new_user),
            "access_token": access_token
        }
        if user.device_id is not None:
            device_token = await auth_service.create_device_token(user, db)
            response_data.update({
                "device_id": user.device_id, "device_token": device_token.token
            })

        return JSONResponse(
            response_data,
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

    new_admin_user = await auth_service.create_user(user=user, db=db)

    if new_admin_user is not None:
        access_token = await auth_service.create_access_token(
            data={"user_id": new_admin_user.id}, db=db
        )

        refresh_token = await auth_service.create_refresh_token(
            data={"user_id": new_admin_user.id}, db=db
        )

        background_tasks.add_task(
            auth_service.send_slack_notification_for_auth,
            new_admin_user,
            "admin signup",
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="172800",
            secure=IS_REFRESH_TOKEN_SECURE,
            httponly=True,
            samesite="strict",
        )

        return JSONResponse(
            {"data": jsonable_encoder(new_admin_user), "access_token": access_token},
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

    # handle mobile login with device id and device token
    if user.email.endswith("[]"):
        device_token = await auth_service.get_device_token(
            device_id=user.email[:-2], device_token=user.password, db=db
        )
        if device_token is None:
            raise fastapi.HTTPException(status_code=403, detail="Invalid credentials")

        userinfo = await auth_service.find_user_by_email(device_token.user_email, db)
        access_token = await auth_service.create_access_token(
            data={"user_id": userinfo["user"].id}, db=db
        )
        refresh_token = await auth_service.create_refresh_token(
            data={"user_id": userinfo["user"].id}, db=db
        )

        background_tasks.add_task(
            auth_service.send_slack_notification_for_auth, userinfo
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="283046400",
            secure=IS_REFRESH_TOKEN_SECURE,
            httponly=True,
            samesite="strict",
        )

    elif user.email:
        userinfo = await auth_service.find_user_by_email(user.email, db)
        if userinfo is None:
            raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")
        veri = userinfo["user"].verify_password(user.password)
        if not veri:
            raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")
        # get or create device token when device id is passed
        if user.device_id is not None:
            device_token = await auth_service.create_device_token(user, db)
        access_token = await auth_service.create_access_token(
            data={"user_id": userinfo["user"].id}, db=db
        )
        refresh_token = await auth_service.create_refresh_token(
            data={"user_id": userinfo["user"].id}, db=db
        )

        background_tasks.add_task(
            auth_service.send_slack_notification_for_auth, userinfo
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="172800",
            secure=IS_REFRESH_TOKEN_SECURE,
            httponly=True,
            samesite="strict",
        )

    elif user.phone_number:
        if user.phone_country_code is None:
            raise fastapi.HTTPException(
                status_code=403,
                detail="you must add country_code when using phone_number to login",
            )
        userinfo = await auth_service.find_user_by_phone(
            user.phone_number, user.phone_country_code, db
        )
        if userinfo is None:
            raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")
        veri = userinfo["user"].verify_password(user.password)
        if not veri:
            raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")
        # get or create device token when device id is passed
        if user.device_id is not None:
            device_token = await auth_service.create_device_token(user, db)
        access_token = await auth_service.create_access_token(
            data={"user_id": userinfo["user"].id}, db=db
        )
        refresh_token = await auth_service.create_refresh_token(
            data={"user_id": userinfo["user"].id}, db=db
        )

        background_tasks.add_task(
            auth_service.send_slack_notification_for_auth, userinfo
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="172800",
            secure=IS_REFRESH_TOKEN_SECURE,
            httponly=True,
            samesite="strict",
        )

    response_data = {"data": userinfo["response_user"], "access_token": access_token}

    if user.device_id or user.email.endswith("[]"):
        response_data.update(
            {"device_token": device_token.token, "device_id": device_token.device_id}
        )

    return response_data


@app.get("/auth/refresh-access-token", status_code=200)
async def refresh_access_token(
    response: Response,
    refresh_token: Union[str, None] = Cookie(default=None),
    db: orm.Session = fastapi.Depends(get_db),
):
    """Refreshes an access_token with the issued refresh_token
    Parameters
        ----------
        refresh_token : str, None
            The refresh token sent in the cookie by the client (default is None)

        Raises
        ------
        UnauthorizedError
            If the refresh token is None.
    """

    credentials_exception = fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if refresh_token is None:
        return fastapi.HTTPException(
            detail="Log in to authenticate user",
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        )

    valid_refresh_token = auth_service.verify_refresh_token(
        refresh_token, credentials_exception, db
    )

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


from uuid import uuid4

# = = = = = = = = = = = = = = = = = = = = = = = = =
# imports
from bigfastapi.models.organization_models import OrganizationInvite, OrganizationUser


@app.post("/auth/sync/user", status_code=201)
async def sync_batch_user(
    user: auth_schemas.UserCreateSync,
    db: orm.Session = fastapi.Depends(get_db),
):
    # Steps:
    # - Create a User in deactivated mode
    # - if user exists update, else create
    # - Send Invite to Organization Invited as accepted
    # - Add User ID to OrganizationUsers

    user__obj = await auth_service.sync_user(user, db=db, is_active=False)
    user_obj = user__obj["data"]

    joined_org = (
        db.query(OrganizationUser)
        .filter(OrganizationUser.user_id == user_obj.id)
        .filter(OrganizationUser.organization_id == user.organization_id)
        .first()
    )

    has_invite = (
        db.query(OrganizationInvite)
        .filter(OrganizationInvite.user_id == user_obj.id)
        .filter(OrganizationInvite.organization_id == user.organization_id)
        .first()
    )

    if user_obj and not has_invite:
        # on bulk - if user and has invite pop out of list and append to update list
        # then do bulk_update_mappings (on update list) and bulk insert mappings (on insert list)
        has_invite = OrganizationInvite(
            id=uuid4().hex,
            organization_id=user.organization_id,
            user_id=user_obj.id,
            email=user_obj.email,
            role_id=user.role_id,
            invite_code=user.password,
            # replicate the invite accepted and deleted
            is_accepted=True,
            is_deleted=True,
        )

        db.add(has_invite)

        if user_obj and not joined_org:
            joined_org = OrganizationUser(
                id=uuid4().hex,
                organization_id=user.organization_id,
                user_id=user_obj.id,
                role_id=user.role_id,
            )

            db.add(joined_org)

        try:
            db.commit()
            db.refresh(has_invite)
            db.refresh(joined_org)

        except Exception as e:
            db.rollback()
            print(e)
            # print or raise exception could not join org

    return JSONResponse(
        {
            "user": jsonable_encoder(user_obj),
            "invite": jsonable_encoder(has_invite),
            "user_org": jsonable_encoder(joined_org),
        },
        status_code=202 if user__obj["updated"] else 201,
    )


@app.get("/auth/sync/user", status_code=201)
async def sync_get_user(
    email: str,
    organization_id: str,
    db: orm.Session = fastapi.Depends(get_db),
):

    # Steps:
    user_obj = (
        db.query(user_models.User).filter(user_models.User.email == email).first()
    )

    if not user_obj:
        return JSONResponse(
            {"error": "User not found"},
            status_code=404,
        )

    joined_org = (
        db.query(OrganizationUser)
        .filter(OrganizationUser.user_id == user_obj.id)
        .filter(OrganizationUser.organization_id == organization_id)
        .first()
    )

    has_invite = (
        db.query(OrganizationInvite)
        .filter(OrganizationInvite.user_id == user_obj.id)
        .filter(OrganizationInvite.organization_id == organization_id)
        .first()
    )

    return JSONResponse(
        {
            "user": jsonable_encoder(user_obj),
            "invite": jsonable_encoder(has_invite),
            "user_org": jsonable_encoder(joined_org),
        },
        status_code=200,
    )


# logout user
@app.get("/auth/{user_id}/logout", status_code=200)
async def logout_user(
    user_id,
    response: Response,
    db: orm.Session = fastapi.Depends(get_db),
):
    # Steps:
    # - Find User
    # - Delete Token
    # - Delete User Cookies
    #  find user by id
    found_user = (
        db.query(user_models.User).filter(user_models.User.id == user_id).first()
    )

    if not found_user:
        return JSONResponse(
            {"error": "User not found"},
            status_code=404,
        )

    # delete refresh token
    token = (
        db.query(auth_models.Token).filter(auth_models.Token.user_id == user_id).first()
    )

    if token:
        db.delete(token)

    try:
        db.commit()

    except Exception as e:
        db.rollback()
        print(e)
        # print or raise exception could not join org

    response.set_cookie(
        key="refresh_token",
        max_age="0",
        secure=IS_REFRESH_TOKEN_SECURE,
        httponly=True,
        samesite="strict",
    )
    return {
        "message": "user logged out",
    }
