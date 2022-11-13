import random
import string
from uuid import uuid4

import fastapi
import passlib.hash as _hash
import sqlalchemy.orm as orm
from authlib.integrations.starlette_client import OAuth
from decouple import config
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from starlette.config import Config

from bigfastapi.db.database import get_db
from bigfastapi.services import auth_service
from bigfastapi.utils import settings

from .models import user_models

app = APIRouter(tags=["Social_Auth"])


# OAuth settings
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException("Missing env variables")

# Set up OAuth
config_data = {
    "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# Set up the middleware to read the request session
SECRET_KEY = settings.JWT_SECRET
BASE_URL = settings.BASE_URL
PYTHON_ENV = config("PYTHON_ENV")

# Redirect response constants
IS_REFRESH_TOKEN_SECURE = True if PYTHON_ENV == "production" else False
REDIRECT_DOMAIN = BASE_URL if PYTHON_ENV == "production" else "localhost"

# Error
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Google oauth error",
    headers={"WWW-Authenticate": "Bearer"},
)


@app.get("/google/generate_url")
async def google_login(request: Request):
    redirect_uri = f"{settings.API_URL}/google/token"
    google_auth_uri = await oauth.google.authorize_redirect(request, redirect_uri)

    # TO-DO: Handle in-session user authentication.
    print(google_auth_uri)

    return {"data": google_auth_uri}
    # return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/google/token")
async def google_auth(request: Request, db: orm.Session = fastapi.Depends(get_db)):

    response = RedirectResponse(f"{settings.BASE_URL}/{settings.CLIENT_REDIRECT_URL}")

    token = await oauth.google.authorize_access_token(request)

    user_data = token["userinfo"]

    check_user = auth_service.valid_email_from_db(user_data["email"], db)

    print(check_user)

    if check_user:
        refresh_token = await auth_service.create_refresh_token(
            data={"user_id": check_user.id}, db=db
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age="172800",
            secure=IS_REFRESH_TOKEN_SECURE,
            httponly=True,
            samesite="strict",
        )

        return response

    S = 10
    ran = "".join(random.choices(string.ascii_uppercase + string.digits, k=S))
    n = str(ran)

    user_obj = user_models.User(
        id=uuid4().hex,
        email=user_data.email,
        password_hash=_hash.sha256_crypt.hash(n),
        first_name=user_data.given_name,
        last_name=user_data.family_name,
        phone_number="",
        is_active=True,
        is_verified=True,
        phone_country_code="",
        is_deleted=False,
        google_id="",
        google_image_url=user_data.picture,
        image_url=user_data.picture,
        device_id="",
    )

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    response = RedirectResponse(f"{settings.BASE_URL}/{settings.CLIENT_REDIRECT_URL}")

    refresh_token = await auth_service.create_refresh_token(
        data={"user_id": user_obj.id}, db=db
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age="172800",
        secure=IS_REFRESH_TOKEN_SECURE,
        httponly=True,
        samesite="strict",
    )

    return response
