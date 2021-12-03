import fastapi as _fastapi
from fastapi import Request
from fastapi.openapi.models import HTTPBearer
import fastapi.security as _security
import jwt as _jwt
import datetime as _dt
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from datetime import datetime, timedelta

from bigfastapi import database as _database, settings as settings
from . import models as _models, schema as _schemas
from fastapi.security import HTTPBearer
bearerSchema = HTTPBearer()
import re
from uuid import uuid4

JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 60 * 60 * 24


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

