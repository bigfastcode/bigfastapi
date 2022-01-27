import fastapi as _fastapi
from fastapi import Request
from fastapi.openapi.models import HTTPBearer
import fastapi.security as _security
import jwt as _jwt
import datetime as _dt
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from datetime import datetime, timedelta
from .models import auth_models
from .models import user_models
from .schemas import auth_schemas
from .schemas import users_schemas
from passlib.context import CryptContext
from bigfastapi.utils import settings as settings
from bigfastapi.db import database as _database

# from . import models as _models, schema as _schemas
from fastapi.security import HTTPBearer
from fastapi.security import OAuth2PasswordBearer
bearerSchema = HTTPBearer()
import re
from uuid import uuid4
import validators
import random
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
# from .users import get_user_by_id, get_user_by_email

from fastapi import APIRouter
from bigfastapi.db.database import get_db

# from bigfastapi.db import database as _database
# from . import models as _models, schema as _schemas
import json
import re
import validators

import requests



JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_IN_MINUTES = 30
ALGORITHM = 'HS256'

app = APIRouter(tags=["Auth"])

@app.post("/auth/signup", status_code=201)
async def create_user(user: auth_schemas.UserCreate, db: _orm.Session = _fastapi.Depends(get_db)): 
    user_email = await find_user_email(user.email, db)
    print(user_email)
    if user_email != None:
        raise _fastapi.HTTPException(status_code=403, detail="Email already exist")        
    user_created = await create_user(user, db=db)
    access_token = await create_access_token(data = {"user_id": user_created.id }, db=db)
    return { "access_token": access_token}


@app.post("/auth/login", status_code=200)
async def login(user: auth_schemas.UserLogin, db: _orm.Session = _fastapi.Depends(get_db)):
    userinfo = await find_user_email(user.email, db)
    veri = userinfo.verify_password(user.password)
    if not veri:
       raise _fastapi.HTTPException(status_code=403, detail="Invalid Credentials")
    
    access_token = await create_access_token(data = {"user_id": userinfo.id }, db=db)
    return {"access_token": access_token}






async def create_user(user: auth_schemas.UserCreate, db: _orm.Session):
    user_obj = user_models.User(
        id = uuid4().hex, email=user.email, password=_hash.sha256_crypt.hash(user.password),
        first_name=user.first_name, last_name=user.last_name, phone_number=user.phone_number,
        is_active=True, is_verified = True
    )
    
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def create_access_token(data: dict, db: _orm.Session):
    to_encode = data.copy()
  
    expire = datetime.utcnow() + timedelta(minutes=1440)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    token_obj = auth_models.Token(id = uuid4().hex, user_id=data["user_id"], token=encoded_jwt)
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception, db: _orm.Session ):
    try:
        #check if token still exist 
        check_token = db.query(auth_models.Token).filter(auth_models.Token.token == token).first()
        if check_token == None:
            raise _fastapi.HTTPException(status_code=403, detail="Invalid Credentials")
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


def is_authenticated(token: str = _fastapi.Depends(oauth2_scheme), db: _orm.Session = _fastapi.Depends(get_db)):
    credentials_exception = _fastapi.HTTPException(status_code=_fastapi.status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credentials_exception, db)
    user = db.query(user_models.User).filter(user_models.User.id == token.id).first()
    return user


async def find_user_email(email, db: _orm.Session):
    found_user = db.query(user_models.User).filter(user_models.User.email == email).first()
    return found_user


def find_country(ctry):
    with open("bigfastapi/data/countries.json") as file:
        cap_country = ctry.capitalize()
        countries = json.load(file)
        found_country = next((country for country in countries if country['name'] == cap_country), None)
        if found_country is None:
            raise _fastapi.HTTPException(status_code=403, detail="This country doesn't exist")
        return found_country['name']


def dialcode(dcode):
    with open("bigfastapi/data/dialcode.json") as file:
        dialcodes = json.load(file)
        found_dialcode = next((dialcode for dialcode in dialcodes if dialcode['dial_code'] == dcode), None)
        if found_dialcode is None:
            raise _fastapi.HTTPException(status_code=403, detail="This is an invalid dialcode")
        return found_dialcode['dial_code']







async def get_code_from_db(code: str, db: _orm.Session):
    return db.query(auth_models.VerificationCode).filter(auth_models.VerificationCode.code == code).first()

async def get_code_by_userid(user_id: str, db: _orm.Session):
    return db.query(auth_models.VerificationCode).filter(auth_models.VerificationCode.user_id == user_id).first()

async def get_password_reset_code_from_db(code: str, db: _orm.Session):
    return db.query(auth_models.PasswordResetCode).filter(auth_models.PasswordResetCode.code == code).first()

async def get_password_reset_code_by_userid(user_id: str, db: _orm.Session):
    return db.query(auth_models.PasswordResetCode).filter(auth_models.PasswordResetCode.user_id == user_id).first()

def generate_code(new_length:int= None):
    length = 6
    if new_length is not None:
        length = new_length
    if length < 4:
        raise _fastapi.HTTPException(status_code=400, detail="Minimum code lenght is 4")
    code = ""
    for i in range(length):
        code += str(random.randint(0,9))
    return code


async def create_verification_code(user: user_models.User, length:int=None):
    user_obj = users_schemas.User.from_orm(user)
    db = _database.SessionLocal()
    code = ""

    db_code = await get_code_by_userid(user_id= user_obj.id, db=db)
    if db_code:
        db.delete(db_code)
        db.commit()
        code = generate_code(length)
        code_obj = auth_models.VerificationCode(id = uuid4().hex, user_id=user_obj.id, code=code)
        db.add(code_obj)
        db.commit()
        db.refresh(code_obj)
    else:
        code = generate_code(length)
        code_obj = auth_models.VerificationCode(id = uuid4().hex, user_id=user_obj.id, code=code)
        db.add(code_obj)
        db.commit()
        db.refresh(code_obj)

    return {"code":code}
    

async def create_forgot_pasword_code(user: user_models.User, length:int=None):
    user_obj = users_schemas.User.from_orm(user)
    db = _database.SessionLocal()
    code = ""

    db_code = db.query(auth_models.PasswordResetCode).filter(auth_models.PasswordResetCode.user_id == user_obj.id).first()
    if db_code:
        db.delete(db_code)
        db.commit()
        code = generate_code(length)
        code_obj = auth_models.PasswordResetCode(id = uuid4().hex, user_id=user_obj.id, code=code)
        db.add(code_obj)
        db.commit()
        db.refresh(code_obj)
    else:
        code = generate_code(length)
        code_obj = auth_models.PasswordResetCode(id = uuid4().hex, user_id=user_obj.id, code=code)
        db.add(code_obj)
        db.commit()
        db.refresh(code_obj)

    return code


async def get_token_from_db(token: str, db: _orm.Session):
    return db.query(auth_models.Token).filter(auth_models.Token.token == token).first()

async def get_token_by_userid(user_id: str, db: _orm.Session):
    return db.query(auth_models.Token).filter(auth_models.Token.user_id == user_id).first()

async def get_header_token(request: Request):
    state = False
    try:
        my_header = request.headers.get('authorization')
        state = True
    except Exception as e:
        state = False

    if not state:
        return {"status": True, "data": "No Authorization token provided"}
    
    try:
        token = my_header.split(" ")[1]
        return {"status": True, "data": token}
    except Exception as e:
        return {"status": True, "data": "Invalid Token"}






async def generate_verification_token(user_id:str, db: _orm.Session):
    payload = {'user_id': user_id}
    token = _jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    token_obj = auth_models.VerificationToken(id = uuid4().hex, user_id=user_id, token=token)
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)
    return token



async def create_verification_token(user: user_models.User):
    user_obj = users_schemas.User.from_orm(user)
    db = _database.SessionLocal()
    token = ""

    db_token = db.query(auth_models.VerificationToken).filter(auth_models.VerificationToken.user_id == user_obj.id).first()
    if db_token:
        validate_resp = await validate_token(db_token.token)
        if not validate_resp["status"]:
            db.delete(db_token)
            db.commit()
            token = await generate_verification_token(user_obj.id, db)
        else:
            token = (db_token.token)
    else:
        token = await generate_verification_token(user_obj.id, db)

    return {"token": token}

    
async def generate_passwordreset_token(user_id:str, db: _orm.Session):
    payload = {'user_id': user_id,
    'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)}
    token = _jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    token_obj = auth_models.PasswordResetToken(id = uuid4().hex, user_id=user_id, token=token)
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)
    return token


async def create_passwordreset_token(user: user_models.User):
    user_obj = users_schemas.User.from_orm(user)
    db = _database.SessionLocal()
    token = ""

    db_token = db.query(auth_models.VerificationToken).filter(auth_models.VerificationToken.user_id == user_obj.id).first()
    if db_token:
        validate_resp = await validate_token(db_token.token)
        if not validate_resp["status"]:
            db.delete(db_token)
            db.commit()
            token = await generate_verification_token(user_obj.id, db)
        else:
            token = (db_token.token)
    else:
        token = await generate_verification_token(user_obj.id, db)

    return {"token": token}


async def logout(user: users_schemas.User):
    db = _database.SessionLocal()
    db_token = await get_token_by_userid(user_id= user.id, db=db)
    print(db_token)
    db.delete(db_token)
    db.commit()
    return True


async def get_user_by_id(id: str, db: _orm.Session):
    return db.query(user_models.User).filter(user_models.User.id == id).first()

async def password_change_code(password: users_schemas.UserPasswordUpdate, code: str, db: _orm.Session):

    code_db = await get_password_reset_code_from_db(code, db)
    if code_db:
        user = await get_user_by_id(db=db, id=code_db.user_id)
        user.password = _hash.sha256_crypt.hash(password.password)
        db.commit()
        db.refresh(user)

        db.delete(code_db)
        db.commit()
        return {"message": "password change successful"}



async def verify_user_token(token:str):
    db = _database.SessionLocal()
    validate_resp = await validate_token(token)
    if not validate_resp["status"]:
        raise _fastapi.HTTPException(
            status_code=401, detail=validate_resp["data"]
        )

    user = await get_user_by_id(db=db, id=validate_resp["data"]["user_id"])
    user.is_verified = True

    db.commit()
    db.refresh(user)

    return users_schemas.User.from_orm(user)


async def password_change_token(password: users_schemas.UserPasswordUpdate, token: str, db: _orm.Session):
    validate_resp = await validate_token(token)
    if not validate_resp["status"]:
        raise _fastapi.HTTPException(
            status_code=401, detail=validate_resp["data"]
        )

    token_db = db.query(auth_models.PasswordResetToken).filter(auth_models.PasswordResetToken.token == token).first()
    if token_db:
        user = await get_user_by_id(db=db, id=validate_resp["data"]["user_id"])
        user.password = _hash.sha256_crypt.hash(password.password)
        db.commit()
        db.refresh(user)

        db.delete(token_db)
        db.commit()
        return {"message": "password change successful"}
    else:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Token")
