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
import validators
import random


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