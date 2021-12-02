import fastapi as _fastapi
from fastapi import Request
from fastapi.openapi.models import HTTPBearer
import fastapi.security as _security
import jwt as _jwt
import datetime as _dt
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from BigFastAPI import database as _database, settings as settings
from . import models as _models, schema as _schemas
from .token import *
from .send_mail import *



from fastapi.security import HTTPBearer
bearerSchema = HTTPBearer()
import re

JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 60 * 5


async def get_user_by_email(email: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.email == email).first()

async def get_user_by_id(id: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.id == id).first()

async def get_orgnanization_by_name(name: str, db: _orm.Session):
    return db.query(_models.Organization).filter(_models.Organization.name == name).first()


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


    


async def create_user(user: _schemas.UserCreate, db: _orm.Session):
    user_obj = _models.User(
        id = uuid4().hex,email=user.email, password=_hash.bcrypt.hash(user.password),
        first_name=user.first_name, last_name=user.last_name,
        is_active=True, is_verified = False
    )
    db.add(user_obj)
    db.commit()
    await resend_verification_mail(user_obj.email,user.verification_redirect_url, db)
    db.refresh(user_obj)
    return user_obj


async def authenticate_user(email: str, password: str, db: _orm.Session):
    user = await get_user_by_email(db=db, email=email)

    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user

async def logout(user: _schemas.User):
    db = _database.SessionLocal()
    db_token = await get_token_by_userid(user_id= user.id, db=db)
    print(db_token)
    db.delete(db_token)
    db.commit()
    return True

async def user_update(user_update: _schemas.UserUpdate, user:_schemas.User, db: _orm.Session):
    user = await get_user_by_id(id = user.id, db=db)

    if user_update.first_name != "":
        user.first_name = user_update.first_name

    if user_update.last_name != "":
        user.last_name = user_update.last_name

    if user_update.phone_number != "":
        user.phone_number = user_update.phone_number
        
    if user_update.organization != "":
        user.organization = user_update.organization

    db.commit()
    db.refresh(user)

    return _schemas.User.from_orm(user)

async def verify_user(token:str):
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

async def password_change(password: _schemas.UserPasswordUpdate, token: str, db: _orm.Session):
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





def validate_email(email):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if(re.search(regex, email)):
        return {"status": True, "message": "Valid"} 
    else:
        return {"status": False, "message": "Enter Valid E-mail"}


async def create_organization(user: _schemas.User, db: _orm.Session, organization: _schemas.OrganizationCreate):
    organization = _models.Organization(id=uuid4().hex, creator=user.id, mission= organization.mission, 
    vision= organization.vision, values= organization.values, name= organization.name)
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return _schemas.Organization.from_orm(organization)


async def get_organizations(user: _schemas.User, db: _orm.Session):
    organizations = db.query(_models.Organization).filter_by(owner_id=user.id)

    return list(map(_schemas.Organization.from_orm, organizations))


async def _organization_selector(organization_id: int, user: _schemas.User, db: _orm.Session):
    organization = (
        db.query(_models.Organization)
        .filter_by(creator=user.id)
        .filter(_models.Organization.id == organization_id)
        .first()
    )

    if organization is None:
        raise _fastapi.HTTPException(status_code=404, detail="Organization does not exist")

    return organization


async def get_organization(organization_id: int, user: _schemas.User, db: _orm.Session):
    organization = await _organization_selector(organization_id=organization_id, user=user, db=db)

    return _schemas.Organization.from_orm(organization)


async def delete_organization(organization_id: int, user: _schemas.User, db: _orm.Session):
    organization = await _organization_selector(organization_id, user, db)

    db.delete(organization)
    db.commit()

async def update_organization(organization_id: int, organization: _schemas.OrganizationUpdate, user: _schemas.User, db: _orm.Session):
    organization_db = await _organization_selector(organization_id, user, db)

    if organization.mission != "":
        organization_db.mission = organization.mission

    if organization.vision != "":
        organization_db.vision = organization.vision

    if organization.values != "":
        organization_db.values = organization.values

    if organization.name != "":
        db_org = await get_orgnanization_by_name(name = organization.name, db=db)
        if db_org:
            raise _fastapi.HTTPException(status_code=400, detail="Organization name already in use")
        else:
            organization_db.name = organization.name       

    organization_db.last_updated = _dt.datetime.utcnow()

    db.commit()
    db.refresh(organization_db)

    return _schemas.Organization.from_orm(organization_db)