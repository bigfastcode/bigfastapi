import fastapi
from fastapi import FastAPI, Request, APIRouter, BackgroundTasks, HTTPException, status
from fastapi.openapi.models import HTTPBearer
import fastapi.security as _security
import passlib.hash as _hash
from .models import auth_models, user_models
from .schemas import auth_schemas, users_schemas
from passlib.context import CryptContext
from bigfastapi.utils import settings, utils
from bigfastapi.db import database as _database
from fastapi.security import OAuth2PasswordBearer
from uuid import uuid4
from bigfastapi.db.database import get_db
import sqlalchemy.orm as orm
from .auth_api import create_access_token
# from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

JWT_SECRET = settings.JWT_SECRET
ALGORITHM = 'HS256'

app = APIRouter(tags=["Auth"])


@app.post("/auth/test", response_model=auth_schemas.TestOut)
async def create_user(user: auth_schemas.TestIn):
    return user

@app.post("/auth/signup", status_code=201)
async def create_user(user: auth_schemas.UserCreate, db: orm.Session = fastapi.Depends(get_db)):
    if user.email == None and user.phone_number == None:
        raise fastapi.HTTPException(status_code=403, detail="you must use a either phone_number or email to sign up") 
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
        
    if user.email or (user.email and user.phone_number):
        user_email = await find_user_email(user.email, db)
        if user_email["user"] != None:
            raise fastapi.HTTPException(status_code=403, detail="Email already exist")
        if(user.phone_number):
            user_phone = await find_user_phone(user.phone_number, user.country_code, db)
            if user_phone["user"] != None:
                raise fastapi.HTTPException(status_code=403, detail="Phone_Number already exist")
        user_created = await create_user(user, db=db)
        access_token = await create_access_token(data = {"user_id": user_created.id }, db=db)
        return { "data": user_created, "access_token": access_token}

    if user.phone_number:
        user_phone = await find_user_phone(user.phone_number, user.country_code, db)
        if user_phone["user"] != None:
            raise fastapi.HTTPException(status_code=403, detail="Phone_Number already exist")
        user_created = await create_user(user, db=db)
        access_token = await create_access_token(data = {"user_id": user_created.id }, db=db)
        return { "data": user_created, "access_token": access_token}
 


@app.post("/auth/login", status_code=200)
async def login(user: auth_schemas.UserLogin, db: orm.Session = fastapi.Depends(get_db)):
    if user.email == None and user.phone_number == None:
        raise fastapi.HTTPException(status_code=403, detail="you must use a either phone_number or email to login") 
    if user.email:    
        userinfo = await find_user_email(user.email, db)
        if userinfo["user"] is None:
            raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")
        veri = userinfo["user"].verify_password(user.password)
        if not veri:
            raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")    
        access_token = await create_access_token(data = {"user_id": userinfo["user"].id }, db=db)  
        return {"data": userinfo["response_user"], "access_token": access_token}
    
    if user.phone_number:
        if user.country_code == None:
            raise fastapi.HTTPException(status_code=403, detail="you must add country_code when using phone_number to login")
        userinfo = await find_user_phone(user.phone_number, user.country_code, db)
        if userinfo["user"] is None:
            raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")
        veri = userinfo["user"].verify_password(user.password)
        if not veri:
            raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")    
        access_token = await create_access_token(data = {"user_id": userinfo["user"].id }, db=db)  
        return {"data": userinfo["response_user"], "access_token": access_token}



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
    return auth_schemas.UserCreateOut.from_orm(user_obj)



async def find_user_email(email, db: orm.Session):
    found_user = db.query(user_models.User).filter(user_models.User.email == email).first()
    return {"user": found_user, "response_user": auth_schemas.UserCreateOut.from_orm(found_user)}


async def find_user_phone(phone_number, country_code, db: orm.Session):
    found_user = db.query(user_models.User).filter(user_models.User.phone_number == phone_number and user_models.User.country_code == country_code).first()
    return {"user": found_user, "response_user": auth_schemas.UserCreateOut.from_orm(found_user)}






