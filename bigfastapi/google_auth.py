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
from starlette.responses import RedirectResponse
import random
import string
from .schemas import google_schema

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

# REDIRECT URL:
# REDIRECT_URL = os.environ.get('REDIRECT_URL') or 'http://127.0.0.1:7001/google/token'
REDIRECT_URL =  'http://127.0.0.1:7001/google/token'

@app.get('/google/generate_url')
async def login(request: Request):
    redirect_uri = REDIRECT_URL  # This creates the url for our /auth endpoint
    response_url = await oauth.google.authorize_redirect(request, redirect_uri)
    return {"data": {"url": response_url._headers['location']}}




# @app.get('/google/token')
# async def auth(request: Request, db: orm.Session = fastapi.Depends(get_db)):
#     try:
#         print("reached callback")
#         access_token = await oauth.google.authorize_access_token(request)
#         return access_token
#     except OAuthError:
#         print('auth error')
#         raise CREDENTIALS_EXCEPTION



# @app.get('/google/auth/{access_token}')
# async def auth_user(access_token: str, db: orm.Session = fastapi.Depends(get_db)):
#     user_data = await oauth.google.parse_id_token(access_token)
    
#     check_user = valid_email_from_db(user_data['email'], db)
    
#     if check_user:
#         print(check_user.id)
#         access_token = await create_access_token(data = {"user_id": check_user.id }, db=db)
#         return { "data": valid_email_from_db(check_user.email, db), "access_token": access_token}

#     S = 10 
#     ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S))  
#     n= str(ran)
    
#     user_obj = user_models.User(
#         id = uuid4().hex, email=user_data.email, password=_hash.sha256_crypt.hash(n),
#         first_name=user_data.given_name, last_name=user_data.family_name, phone_number="",
#         is_active=True, is_verified = True, country_code="", is_deleted=False,
#         country="", state= "", google_id = "", google_image=user_data.picture,
#         image = user_data.picture, device_id = ""
#     )
#     print("creating a user")
    
#     db.add(user_obj)
#     db.commit()
#     db.refresh(user_obj)

#     access_token = await create_access_token(data = {"user_id": user_obj.id }, db=db)
#     return { "data": valid_email_from_db(user_obj.email, db), "access_token": access_token}


@app.get('/google/token')
async def auth(request: Request, db: orm.Session = fastapi.Depends(get_db)):
    try:
        access_token = await oauth.google.authorize_access_token(request)
        user_data = await oauth.google.parse_id_token(request, access_token)
        check_user = valid_email_from_db(user_data['email'], db)
    
        if check_user:
            user_id = str(check_user.id)
            access_token = await create_access_token(data = {"user_id": check_user.id }, db=db)
            response = f"http://127.0.0.1:8000/google/authenticate?token={access_token}&user_id={user_id}"            
            print(response)
            return RedirectResponse(url=response)       


        S = 10 
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S))  
        n= str(ran)
    
        user_obj = user_models.User(
            id = uuid4().hex, email=user_data.email, password=_hash.sha256_crypt.hash(n),
            first_name=user_data.given_name, last_name=user_data.family_name, phone_number=null,
            is_active=True, is_verified = True, country_code="", is_deleted=False,
            country="", state= "", google_id = "", google_image=user_data.picture,
            image = user_data.picture, device_id = ""
        )

        print("creating a user")
    
        db.add(user_obj)
        db.commit()
        db.refresh(user_obj)

        response = 'http://127.0.0.1:8000/google/authenticate?token=' + access_token["id_token"] + '&user_id=' + user_obj.id
        print(response)
        return RedirectResponse(url=response)
    except OAuthError:
        return RedirectResponse(url='http://127.0.0.1:8000/signup')

    
@app.post('/google/validate-token')
async def validate_user(user: google_schema.GoogleAuth,  db: orm.Session = fastapi.Depends(get_db)):
    user_found = db.query(user_models.User).filter(user_models.User.id == user.user_id).first()
    return {"data": user_found, "access_token": user.token}



# @app.get('/google/token/')
# async def auth(request: Request, db: orm.Session = fastapi.Depends(get_db)):
#     try:
#         print("reached callback")
#         access_token = await oauth.google.authorize_access_token(request)
#     except OAuthError:
#         print('auth error')
#         raise CREDENTIALS_EXCEPTION
#     user_data = await oauth.google.parse_id_token(request, access_token)
    
#     check_user = valid_email_from_db(user_data['email'], db)
    
#     if check_user:
#         print(check_user.id)
#         access_token = await create_access_token(data = {"user_id": check_user.id }, db=db)
#         return { "data": valid_email_from_db(check_user.email, db), "access_token": access_token}

#     S = 10 
#     ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S))  
#     n= str(ran)
    
#     user_obj = user_models.User(
#         id = uuid4().hex, email=user_data.email, password=_hash.sha256_crypt.hash(n),
#         first_name=user_data.given_name, last_name=user_data.family_name, phone_number="",
#         is_active=True, is_verified = True, country_code="", is_deleted=False,
#         country="", state= "", google_id = "", google_image=user_data.picture,
#         image = user_data.picture, device_id = ""
#     )
#     print("creating a user")
    
#     db.add(user_obj)
#     db.commit()
#     db.refresh(user_obj)

#     access_token = await create_access_token(data = {"user_id": user_obj.id }, db=db)
#     return { "data": valid_email_from_db(user_obj.email, db), "access_token": access_token}





def valid_email_from_db(email, db: orm.Session = fastapi.Depends(get_db)):
    found_user = db.query(user_models.User).filter(user_models.User.email == email).first()
    return found_user


# https://v2.customerpay.me/app/google/authenticate?
# token=eyJhbGciOiJSUzI1NiIsImtpZCI6IjE4MmU0NTBhMzVhMjA4MWZhYTFkOWFlMWQyZDc1YTBmMjNkOTFkZjgiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI2MjA4MjQ4MTM2NzEtNDdxOWZjdDlvbTQwMzNoNnAycG42bjNlbTNubXViNHMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI2MjA4MjQ4MTM2NzEtNDdxOWZjdDlvbTQwMzNoNnAycG42bjNlbTNubXViNHMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDIwMDA0NTEwMTE1NTE0NzAxMjUiLCJlbWFpbCI6ImRpc3V0akBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXRfaGFzaCI6ImJGVFhTWnctXzhaZGQ2eXBabmZrWmciLCJub25jZSI6ImJFZWxFNjVGMkRYdFJNR2JWU3pOIiwibmFtZSI6IkRpc3UgT2x1d2F0b3lpbiIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS0vQU9oMTRHaTlfV1lMdXZEVF9mWUdkYnUzTTdDcU5yNDg3dDVUYU9YR19LWk5CQT1zOTYtYyIsImdpdmVuX25hbWUiOiJEaXN1IiwiZmFtaWx5X25hbWUiOiJPbHV3YXRveWluIiwibG9jYWxlIjoiZW4iLCJpYXQiOjE2NDQ1MDE0MjAsImV4cCI6MTY0NDUwNTAyMH0.DZeVcEpFB_8Ea5HUUlP6fPFRT2BV_ED3XkbFsY-Fph34MenpURgyUiEhRiGD3l_bVv6KgD5YoYlTEyW4kcxMYdQOkh5nB_ZT5js6A4_Jtbuu49UuuZW5f2jR_lUthfwuc9aClMIr7XSXWggmPR7EXX75sF6ZtCmsCE33YjrKt7K2vqNHMb-Y6cg80v0feqkST6-JlKbY945E-3buKt3X_GfidFTtttDcYx4V4TqKgjpTYCHv7zh2pPGyJpRUoTH8T5YVRZ6pr7AwJ4MSK5X91SeG2sGdGYEvQQc4iX-lgU5nRiZTvvYyVCsvdMRo0emOETBT3oh8kFepJ27PbnB87Q
# &user_id=29876542909876542#