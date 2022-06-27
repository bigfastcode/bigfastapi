
from datetime import datetime, timedelta
from uuid import uuid4

import fastapi
import jwt
from bigfastapi.core.helpers import Helpers
from bigfastapi.models import auth_models, user_models
from bigfastapi.schemas import auth_schemas
import sqlalchemy.orm as orm
import passlib.hash as _hash

from bigfastapi.utils import settings, utils


JWT_SECRET = settings.JWT_SECRET
ALGORITHM = 'HS256'


def create_user(user: auth_schemas.UserCreate, db:  orm.Session, is_su: bool = False):
    su_status = True if is_su else False

    previousInstance = db.query(user_models.User).filter(
        user_models.User.email == user.email).first()
    if previousInstance:
        raise fastapi.HTTPException(
            status_code=422, detail=f"Account with {user.email} already exist")

    if user.phone_number and user.country_code == None:
        raise fastapi.HTTPException(
            status_code=422, detail="country code is required")
    if user.phone_number and user.country_code:
        if utils.dialcode(user.country_code) is None:
            raise fastapi.HTTPException(
                status_code=422, detail="invalid country code")

    user_obj = user_models.User(
        id=uuid4().hex, email=user.email, password=_hash.sha256_crypt.hash(user.password),
        first_name=user.first_name, last_name=user.last_name, phone_number=user.phone_number,
        is_active=True, is_verified=True, is_superuser=su_status, country_code=user.country_code, is_deleted=False,
        country=user.country, state=user.state, google_id=user.google_id, google_image=user.google_image,
        image=user.image, device_id=user.device_id
    )

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return auth_schemas.UserCreateOut.from_orm(user_obj)


def create_access_token(data: dict, db: orm.Session):
    print("I GOT HERE")
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=1440)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    token_obj = auth_models.Token(
        id=uuid4().hex, user_id=data["user_id"], token=encoded_jwt)
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)
    return encoded_jwt


def send_slack_notification(user):
    message = "New login from " + user.email
    # sends the message to slack
    Helpers.slack_notification("LOG_WEBHOOK_URL", text=message)
