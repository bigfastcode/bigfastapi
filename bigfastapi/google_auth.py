import os
import fastapi
from pytest import Session
from sqlalchemy import null
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
from bigfastapi.db.database import get_db
from bigfastapi.auth_api import create_access_token
from bigfastapi.utils import settings
from starlette.responses import RedirectResponse, HTMLResponse
import random
import string
from .schemas import google_schema, auth_schemas

app = APIRouter(tags=["Social_Auth"])


# OAuth settings
GOOGLE_CLIENT_ID=settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=settings.GOOGLE_CLIENT_SECRET
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
SECRET_KEY = settings.JWT_SECRET

# Error
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Google oauth error',
    headers={'WWW-Authenticate': 'Bearer'},
)


REDIRECT_URL =  'https://v2.api.customerpay.me/google/token'


@app.get('/google/generate_url')
async def login(request: Request):
    redirect_uri = REDIRECT_URL  # This creates the url for our /auth endpoint
    return await oauth.google.authorize_redirect(request, redirect_uri)



@app.get('/google/token')
async def auth(request: Request, db: orm.Session = fastapi.Depends(get_db)):

    access_token = await oauth.google.authorize_access_token(request)
    user_data = await oauth.google.parse_id_token(request, access_token)
    check_user = valid_email_from_db(user_data['email'], db)
    
    if check_user:
        user_id = str(check_user.id)
        access_token = await create_access_token(data = {"user_id": check_user.id }, db=db)
        response = f"https://v2.customerpay.me/app/google/authenticate?token={access_token}&user_id={user_id}"            
    
        return RedirectResponse(url=response)       


    S = 10 
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S))  
    n= str(ran)
    
    user_obj = user_models.User(
        id = uuid4().hex, email=user_data.email, password=_hash.sha256_crypt.hash(n),
        first_name=user_data.given_name, last_name=user_data.family_name, phone_number=n,
        is_active=True, is_verified = True, country_code="", is_deleted=False,
        country="", state= "", google_id = "", google_image=user_data.picture,
        image = user_data.picture, device_id = ""
    )

  
    
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    response = 'https://v2.customerpay.me/app/google/authenticate?token=' + access_token["id_token"] + '&user_id=' + user_obj.id
    return RedirectResponse(url=response)



    
@app.post('/google/validate-token')
async def validate_user(user: google_schema.GoogleAuth,  db: orm.Session = fastapi.Depends(get_db)):
    user_found = db.query(user_models.User).filter(user_models.User.id == user.user_id).first()
    return {"data":  auth_schemas.UserCreateOut.from_orm(user_found), "access_token": user.token}



def valid_email_from_db(email, db: orm.Session = fastapi.Depends(get_db)):
    found_user = db.query(user_models.User).filter(user_models.User.email == email).first()
    return found_user


