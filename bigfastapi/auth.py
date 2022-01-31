import fastapi
from fastapi import Request, APIRouter, BackgroundTasks
from fastapi.openapi.models import HTTPBearer
import fastapi.security as _security
import jwt as _jwt
import datetime as _dt
import passlib.hash as _hash
from datetime import datetime, timedelta
from .models import auth_models, user_models
from .schemas import auth_schemas, users_schemas
from passlib.context import CryptContext
from bigfastapi.utils import settings, utils
from bigfastapi.db import database as _database
from fastapi.security import OAuth2PasswordBearer
from uuid import uuid4
import random
from jose import JWTError, jwt
from bigfastapi.db.database import get_db
import json
import re
import validators
import requests
from bigfastapi.email import conf
from fastapi_mail import FastMail, MessageSchema
import sqlalchemy.orm as orm


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

JWT_SECRET = settings.JWT_SECRET
ALGORITHM = 'HS256'

app = APIRouter(tags=["Auth"])

@app.post("/auth/signup", status_code=201)
async def create_user(user: auth_schemas.UserCreate, db: orm.Session = fastapi.Depends(get_db)): 
    if user.phone_number and user.country_code == None:
        raise fastapi.HTTPException(status_code=403, detail="you must add a country code when you add a phone number") 
    if user.phone_number and user.country_code:
        check_contry_code = utils.dialcode(user.country_code)
        if check_contry_code is None:
            raise fastapi.HTTPException(status_code=403, detail="this country code is invalid")
    if user.phone_number == None and user.country_code:
        raise fastapi.HTTPException(status_code=403, detail="you must add a phone number when you add a country code")
    if user.country:
        check_country = utils.find_country(user.country)
        if check_country is None:
            raise fastapi.HTTPException(status_code=403, detail="this country is invalid")

    user_email = await find_user_email(user.email, db)
    if user_email != None:
        raise fastapi.HTTPException(status_code=403, detail="Email already exist")        
    user_created = await create_user(user, db=db)
    access_token = await create_access_token(data = {"user_id": user_created.id }, db=db)
    return { "access_token": access_token}


@app.post("/auth/login", status_code=200)
async def login(user: auth_schemas.UserLogin, db: orm.Session = fastapi.Depends(get_db)):
    userinfo = await find_user_email(user.email, db)
    if userinfo is None:
        raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")
    veri = userinfo.verify_password(user.password)
    if not veri:
       raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")
    
    access_token = await create_access_token(data = {"user_id": userinfo.id }, db=db)
    return {"access_token": access_token}


async def create_user(user: auth_schemas.UserCreate, db: orm.Session):
    user_obj = user_models.User(
        id = uuid4().hex, email=user.email, password=_hash.sha256_crypt.hash(user.password),
        first_name=user.first_name, last_name=user.last_name, phone_number=user.phone_number,
        is_active=True, is_verified = True, country_code=user.country_code, is_deleted=False,
        country=user.country, state= user.state, google_id = user.google_id, google_image= user.google_image,
        image = user.image, device_id = user.device_id
    )
    
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def create_access_token(data: dict, db: orm.Session):
    to_encode = data.copy()
  
    expire = datetime.utcnow() + timedelta(minutes=1440)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    token_obj = auth_models.Token(id = uuid4().hex, user_id=data["user_id"], token=encoded_jwt)
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception, db: orm.Session ):
    try:
        #check if token still exist 
        check_token = db.query(auth_models.Token).filter(auth_models.Token.token == token).first()
        if check_token == None:
            raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        user = db.query(user_models.User).filter(user_models.User.id == id).first()
        email = user.email
        if id is None:
            raise credentials_exception
        token_data = auth_schemas.TokenData(email=email, id=id)
    except JWTError:
        raise credentials_exception

    return token_data


def is_authenticated(token: str = fastapi.Depends(oauth2_scheme), db: orm.Session = fastapi.Depends(get_db)):
    credentials_exception = fastapi.HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credentials_exception, db)
    user = db.query(user_models.User).filter(user_models.User.id == token.id).first()
    return user


async def find_user_email(email, db: orm.Session):
    found_user = db.query(user_models.User).filter(user_models.User.email == email).first()
    return found_user




