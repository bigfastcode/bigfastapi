import fastapi
from fastapi import Request
from fastapi.openapi.models import HTTPBearer
import fastapi.security as _security
import jwt as _jwt
import datetime as _dt
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from datetime import datetime, timedelta
from .models import auth_models, user_models
from .schemas import auth_schemas, users_schemas
from passlib.context import CryptContext
from bigfastapi.utils import settings as settings
from bigfastapi.db import database as _database
from fastapi.security import OAuth2PasswordBearer
from uuid import uuid4
import validators
import random
from jose import JWTError, jwt
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
from fastapi import APIRouter
from bigfastapi.db.database import get_db
import json
import re
import validators
import requests

from bigfastapi.email import conf
from fastapi_mail import FastMail, MessageSchema
import sqlalchemy.orm as orm
import fastapi
from fastapi import BackgroundTasks



JWT_SECRET = settings.JWT_SECRET
ALGORITHM = 'HS256'

app = APIRouter(tags=["Auth"])

@app.post("/auth/signup", status_code=201)
async def create_user(user: auth_schemas.UserCreate, db: _orm.Session = fastapi.Depends(get_db)): 
    if user.phone_number and user.country_code == None:
        raise fastapi.HTTPException(status_code=403, detail="you must add a country code when you add a phone number") 
    if user.phone_number and user.country_code:
        check_contry_code = dialcode(user.country_code)
        if check_contry_code is None:
            raise fastapi.HTTPException(status_code=403, detail="this country code is invalid")
    if user.phone_number == None and user.country_code:
        raise fastapi.HTTPException(status_code=403, detail="you must add a phone number when you add a country code")
    if user.country:
        check_country = find_country(user.country)
        if check_country is None:
            raise fastapi.HTTPException(status_code=403, detail="this country is invalid")

    user_email = await find_user_email(user.email, db)
    if user_email != None:
        raise fastapi.HTTPException(status_code=403, detail="Email already exist")        
    user_created = await create_user(user, db=db)
    access_token = await create_access_token(data = {"user_id": user_created.id }, db=db)
    return { "access_token": access_token}


@app.post("/auth/login", status_code=200)
async def login(user: auth_schemas.UserLogin, db: _orm.Session = fastapi.Depends(get_db)):
    userinfo = await find_user_email(user.email, db)
    veri = userinfo.verify_password(user.password)
    if not veri:
       raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")
    
    access_token = await create_access_token(data = {"user_id": userinfo.id }, db=db)
    return {"access_token": access_token}






async def create_user(user: auth_schemas.UserCreate, db: _orm.Session):
    user_obj = user_models.User(
        id = uuid4().hex, email=user.email, password=_hash.sha256_crypt.hash(user.password),
        first_name=user.first_name, last_name=user.last_name, phone_number=user.phone_number,
        is_active=True, is_verified = True, country_code=user.country_code, is_deleted=False,
        country=user.country, state= user.state, 
        image = user.image, device_id = user.device_id
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


def is_authenticated(token: str = fastapi.Depends(oauth2_scheme), db: _orm.Session = fastapi.Depends(get_db)):
    credentials_exception = fastapi.HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
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
            raise fastapi.HTTPException(status_code=403, detail="This country doesn't exist")
        return found_country['name']


def dialcode(dcode):
    with open("bigfastapi/data/dialcode.json") as file:
        dialcodes = json.load(file)
        found_dialcode = next((dialcode for dialcode in dialcodes if dialcode['dial_code'] == dcode), None)
        if found_dialcode is None:
            raise fastapi.HTTPException(status_code=403, detail="This is an invalid dialcode")
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
        raise fastapi.HTTPException(status_code=400, detail="Minimum code lenght is 4")
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
        raise fastapi.HTTPException(
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
        raise fastapi.HTTPException(
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
        raise fastapi.HTTPException(status_code=401, detail="Invalid Token")



######################### DEFAULT AUTH MAIL SERVICES #####################################


async def get_user_by_email(email: str, db: orm.Session):
    return db.query(user_models.User).filter(user_models.User.email == email).first()


async def send_code_password_reset_email(
    email: str, db: orm.Session, codelength: int = None
):
    user = await get_user_by_email(email, db)
    if user:
        code = await create_forgot_pasword_code(user, codelength)
        message = MessageSchema(
            subject="Password Reset",
            recipients=[email],
            template_body={
                "title": "Change your password",
                "first_name": user.first_name,
                "code": code["code"],
            },
            subtype="html",
        )
        await send_email_async(message, settings.PASSWORD_RESET_TEMPLATE)
        return {"code": code["code"]}
    else:
        raise fastapi.HTTPException(status_code=401, detail="Email not registered")


async def resend_code_verification_mail(
    email: str, db: orm.Session, codelength: int = None
):
    user = await get_user_by_email(email, db)
    if user:
        code = await create_verification_code(user, codelength)
        message = MessageSchema(
            subject="Email Verification",
            recipients=[email],
            template_body={
                "title": "Verify Your Account",
                "first_name": user.first_name,
                "code": code["code"],
            },
            subtype="html",
        )
        await send_email_async(message, settings.EMAIL_VERIFICATION_TEMPLATE)
        return {"code": code["code"]}
    else:
        raise fastapi.HTTPException(status_code=401, detail="Email not registered")


async def send_token_password_reset_email(
    email: str, redirect_url: str, db: orm.Session
):
    user = await get_user_by_email(email, db)
    if user:
        token = await create_passwordreset_token(user)
        path = "{}/?token={}".format(redirect_url, token["token"])
        message = MessageSchema(
            subject="Password Reset",
            recipients=[email],
            template_body={
                "title": "Change you",
                "first_name": user.first_name,
                "path": path,
            },
            subtype="html",
        )
        await send_email_async(message, settings.PASSWORD_RESET_TEMPLATE)
        return {"token": token}
    else:
        raise fastapi.HTTPException(status_code=401, detail="Email not registered")


async def resend_token_verification_mail(
    email: str, redirect_url: str, db: orm.Session
):
    user = await get_user_by_email(email, db)
    if user:
        token = await create_verification_token(user)
        path = "{}/?token={}".format(redirect_url, token["token"])
        message = MessageSchema(
            subject="Email Verification",
            recipients=[email],
            template_body={
                "title": "Verify Your Account",
                "first_name": user.first_name,
                "path": path,
            },
            subtype="html",
        )
        await send_email_async(message, settings.EMAIL_VERIFICATION_TEMPLATE)
        return {"token": token}
    else:
        raise fastapi.HTTPException(status_code=401, detail="Email not registered")


async def send_email_async(message: MessageSchema, template: str):
    fm = FastMail(conf)
    await fm.send_message(message, template_name=template)


def send_email_background(
    background_tasks: BackgroundTasks, message: MessageSchema, template: str
):
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message, template_name="email.html") 


