import fastapi as _fastapi
from fastapi import Request
from fastapi.openapi.models import HTTPBearer
import fastapi.security as _security
import jwt as _jwt
import datetime as _dt
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from datetime import datetime, timedelta

from bigfastapi.utils import settings as settings
from bigfastapi.db import database as _database
from . import models as _models, schema as _schemas
from fastapi.security import HTTPBearer
bearerSchema = HTTPBearer()
import re
from uuid import uuid4
import validators
import random

import fastapi as _fastapi
from fastapi import Request
from fastapi.openapi.models import HTTPBearer
import fastapi.security as _security
import jwt as _jwt
import datetime as _dt
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from datetime import datetime, timedelta

from bigfastapi.utils import settings as settings
from bigfastapi.db import database as _database
from . import models as _models, schema as _schemas
from fastapi.security import HTTPBearer
bearerSchema = HTTPBearer()
import re
from uuid import uuid4
import validators


JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 60 * 60 * 24

JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 60 * 60 * 24


async def get_code_from_db(code: str, db: _orm.Session):
    return db.query(_models.VerificationCode).filter(_models.VerificationCode.code == code).first()

async def get_code_by_userid(user_id: str, db: _orm.Session):
    return db.query(_models.VerificationCode).filter(_models.VerificationCode.user_id == user_id).first()
async def get_password_reset_code_from_db(code: str, db: _orm.Session):
    return db.query(_models.PasswordResetCode).filter(_models.PasswordResetCode.code == code).first()

async def get_password_reset_code_by_userid(user_id: str, db: _orm.Session):
    return db.query(_models.PasswordResetCode).filter(_models.PasswordResetCode.user_id == user_id).first()

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


async def create_verification_code(user: _models.User, length:int=None):
    user_obj = _schemas.User.from_orm(user)
    db = _database.SessionLocal()
    code = ""

    db_code = await get_code_by_userid(user_id= user_obj.id, db=db)
    if db_code:
        db.delete(db_code)
        db.commit()
        code = generate_code(length)
        code_obj = _models.VerificationCode(id = uuid4().hex, user_id=user_obj.id, code=code)
        db.add(code_obj)
        db.commit()
        db.refresh(code_obj)
    else:
        code = generate_code(length)
        code_obj = _models.VerificationCode(id = uuid4().hex, user_id=user_obj.id, code=code)
        db.add(code_obj)
        db.commit()
        db.refresh(code_obj)

    return {"code":code}

async def create_forgot_pasword_code(user: _models.User, length:int=None):
    user_obj = _schemas.User.from_orm(user)
    db = _database.SessionLocal()
    code = ""

    db_code = db.query(_models.PasswordResetCode).filter(_models.PasswordResetCode.user_id == user_obj.id).first()
    if db_code:
        db.delete(db_code)
        db.commit()
        code = generate_code(length)
        code_obj = _models.PasswordResetCode(id = uuid4().hex, user_id=user_obj.id, code=code)
        db.add(code_obj)
        db.commit()
        db.refresh(code_obj)
    else:
        code = generate_code(length)
        code_obj = _models.PasswordResetCode(id = uuid4().hex, user_id=user_obj.id, code=code)
        db.add(code_obj)
        db.commit()
        db.refresh(code_obj)

    return {"code":code}



def ValidateUrl(url):
    valid=validators.url(url)
    if valid==True:
        return True
    else:
        return False



async def get_token_from_db(token: str, db: _orm.Session):
    return db.query(_models.Token).filter(_models.Token.token == token).first()

async def get_token_by_userid(user_id: str, db: _orm.Session):
    return db.query(_models.Token).filter(_models.Token.user_id == user_id).first()

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

async def validate_token(token: str):
    try:
        data = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except _jwt.ExpiredSignatureError:
        return {"status": False, "data": "token has expired"}
    except Exception as e:
        return {"status": False, "data": "Invalid Token"}

    return {"status": True, "data": data}


async def generate_token(user_id:str, db: _orm.Session):
    payload = {'user_id': user_id,
    'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)}
    token = _jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    token_obj = _models.Token(id = uuid4().hex, user_id=user_id, token=token)
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)
    return token

async def create_token(user: _models.User):
    user_obj = _schemas.User.from_orm(user)
    db = _database.SessionLocal()
    token = ""

    db_token = await get_token_by_userid(user_id= user_obj.id, db=db)
    # token_obj = _schemas.User.from_orm(db_token)
    if db_token:
        validate_resp = await validate_token(db_token.token)
        if not validate_resp["status"]:
            db.delete(db_token)
            db.commit()
            token = await generate_token(user_obj.id, db)
        else:
            token = (db_token.token)
    else:
        token = await generate_token(user_obj.id, db)

    return dict(access_token=token, token_type="bearer")


async def generate_verification_token(user_id:str, db: _orm.Session):
    payload = {'user_id': user_id}
    token = _jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    token_obj = _models.VerificationToken(id = uuid4().hex, user_id=user_id, token=token)
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)
    return token



async def create_verification_token(user: _models.User):
    user_obj = _schemas.User.from_orm(user)
    db = _database.SessionLocal()
    token = ""

    db_token = db.query(_models.VerificationToken).filter(_models.VerificationToken.user_id == user_obj.id).first()
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
    token_obj = _models.PasswordResetToken(id = uuid4().hex, user_id=user_id, token=token)
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)
    return token


async def create_passwordreset_token(user: _models.User):
    user_obj = _schemas.User.from_orm(user)
    db = _database.SessionLocal()
    token = ""

    db_token = db.query(_models.VerificationToken).filter(_models.VerificationToken.user_id == user_obj.id).first()
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


async def logout(user: _schemas.User):
    db = _database.SessionLocal()
    db_token = await get_token_by_userid(user_id= user.id, db=db)
    print(db_token)
    db.delete(db_token)
    db.commit()
    return True

async def verify_user_code(code:str):
    db = _database.SessionLocal()
    code_db = await get_code_from_db(code, db)
    if code_db:
        user = await get_user_by_id(db=db, id=code_db.user_id)
        user.is_verified = True

        db.commit()
        db.refresh(user)
        db.delete(code_db)
        db.commit()
        return _schemas.User.from_orm(user)
    else:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Code")

async def authenticate_user(email: str, password: str, db: _orm.Session):
    user = await get_user_by_email(db=db, email=email)

    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user

async def is_authenticated(request: Request, token:str = _fastapi.Depends(bearerSchema), db: _orm.Session = _fastapi.Depends(_database.get_db)):
    token = token.credentials
    validate_resp = await validate_token(token)
    if not validate_resp["status"]:
        raise _fastapi.HTTPException(
            status_code=401, detail=validate_resp["data"]
        )

    user = await get_user_by_id(db=db, id=validate_resp["data"]["user_id"])
    db_token = await get_token_from_db(token, db)
    if db_token:
        return _schemas.User.from_orm(user)
    else:
        raise _fastapi.HTTPException(
            status_code=401, detail="invalid token"
        )


async def password_change_code(password: _schemas.UserPasswordUpdate, code: str, db: _orm.Session):

    code_db = await get_password_reset_code_from_db(code, db)
    if code_db:
        user = await get_user_by_id(db=db, id=code_db.user_id)
        user.password = _hash.bcrypt.hash(password.password)
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

    return _schemas.User.from_orm(user)


async def password_change_token(password: _schemas.UserPasswordUpdate, token: str, db: _orm.Session):
    validate_resp = await validate_token(token)
    if not validate_resp["status"]:
        raise _fastapi.HTTPException(
            status_code=401, detail=validate_resp["data"]
        )

    token_db = db.query(_models.PasswordResetToken).filter(_models.PasswordResetToken.token == token).first()
    if token_db:
        user = await get_user_by_id(db=db, id=validate_resp["data"]["user_id"])
        user.password = _hash.bcrypt.hash(password.password)
        db.commit()
        db.refresh(user)

        db.delete(token_db)
        db.commit()
        return {"message": "password change successful"}
    else:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Token")



