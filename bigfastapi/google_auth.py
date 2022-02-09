import os
import fastapi
from pytest import Session
from .models import auth_models, user_models
from datetime import datetime
from datetime import timedelta
import sqlalchemy.orm as orm
import jwt
from uuid import uuid4
from fastapi import Depends, APIRouter
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
import passlib.hash as _hash
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse
from bigfastapi.db.database import get_db
from bigfastapi.auth_api import create_access_token


app = APIRouter(tags=["Social_Auth"])


# OAuth settings
GOOGLE_CLIENT_ID="620824813671-47q9fct9om4033h6p2pn6n3em3nmub4s.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="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"
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException('Missing env variables')

# Set up OAuth
config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

# Set up the middleware to read the request session
SECRET_KEY = "yeahyeh500500"
if SECRET_KEY is None:
    raise 'Missing SECRET_KEY'



# Frontend URL:
FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://127.0.0.1:7001/google/token'


@app.get('/google/generate_url')
async def login(request: Request):
    redirect_uri = FRONTEND_URL  # This creates the url for our /auth endpoint
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get('/google/token')
async def auth(request: Request, db: orm.Session = fastapi.Depends(get_db)):
    try:
        
        print("USER AUTH")
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise CREDENTIALS_EXCEPTION
    user_data = await oauth.google.parse_id_token(request, access_token)
    
    check_user = valid_email_from_db(user_data['email'], db)
    
    if check_user:
        print(check_user.id)
        access_token = await create_access_token(data = {"user_id": check_user.id }, db=db)
        return { "data": valid_email_from_db(check_user.email, db), "access_token": access_token}

    user_obj = user_models.User(
        id = uuid4().hex, email=user_data.email, password=_hash.sha256_crypt.hash(user_data.at_hash),
        first_name=user_data.given_name, last_name=user_data.family_name, phone_number="",
        is_active=True, is_verified = True, country_code="", is_deleted=False,
        country="", state= "", google_id = "", google_image=user_data.picture,
        image = user_data.picture, device_id = ""
    )
    print("creating a user")
    
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    access_token = await create_access_token(data = {"user_id": user_obj.id }, db=db)
    return { "data": valid_email_from_db(user_obj.email, db), "access_token": access_token}



def cast_to_number(id):
    temp = os.environ.get(id)
    if temp is not None:
        try:
            return float(temp)
        except ValueError:
            return None
    return None


# Configuration
API_SECRET_KEY = "uyyeujnfbhgdtwyuiofkjhndbwgyufiklew"
if API_SECRET_KEY is None:
    raise BaseException('Missing API_SECRET_KEY env var.')
API_ALGORITHM = os.environ.get('API_ALGORITHM') or 'HS256'
API_ACCESS_TOKEN_EXPIRE_MINUTES = cast_to_number('API_ACCESS_TOKEN_EXPIRE_MINUTES') or 1444

# Token url (We should later create a token url that accepts just a user and a password to use it with Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')

# Error
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={'WWW-Authenticate': 'Bearer'},
)


def valid_email_from_db(email, db: orm.Session = fastapi.Depends(get_db)):
    found_user = db.query(user_models.User).filter(user_models.User.email == email).first()
    return found_user


async def get_current_user_email(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, API_SECRET_KEY, algorithms=[API_ALGORITHM])
        email: str = payload.get('sub')
        if email is None:
            raise CREDENTIALS_EXCEPTION
    except jwt.PyJWTError:
        raise CREDENTIALS_EXCEPTION

    if valid_email_from_db(email, db=orm.Session):
        return email

    raise CREDENTIALS_EXCEPTION
