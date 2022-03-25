import fastapi
from fastapi import Request, APIRouter, BackgroundTasks
import jwt as _jwt
import passlib.hash as _hash
from datetime import datetime, timedelta
from .models import auth_models, user_models
from .schemas import auth_schemas, users_schemas
from passlib.context import CryptContext
from bigfastapi.utils import settings
from bigfastapi.db import database as _database
from fastapi.security import OAuth2PasswordBearer
from uuid import uuid4
import random
from jose import JWTError, jwt
from bigfastapi.db.database import get_db
import sqlalchemy.orm as orm
from .email import send_email_user
# from .users import get_user

app = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = settings.JWT_SECRET
ALGORITHM = 'HS256'


async def create_access_token(data: dict, db: orm.Session):
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


def verify_access_token(token: str, credentials_exception, db: orm.Session):
    try:
        # check if token still exist
        check_token = db.query(auth_models.Token).filter(
            auth_models.Token.token == token).first()
        if check_token == None:
            raise fastapi.HTTPException(
                status_code=403, detail="Invalid Credentials")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        user = db.query(user_models.User).filter(
            user_models.User.id == id).first()
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
    user = db.query(user_models.User).filter(
        user_models.User.id == token.id).first()
    return user


def generate_code(new_length: int = None):
    length = 6
    if new_length is not None:
        length = new_length
    if length < 4:
        raise fastapi.HTTPException(
            status_code=400, detail="Minimum code lenght is 4")
    code = ""
    for i in range(length):
        code += str(random.randint(0, 9))
    return code


async def create_verification_code(user: user_models.User, length: int = None):
    user_obj = users_schemas.User.from_orm(user)
    db = _database.SessionLocal()
    code = ""
    db_code = await get_code_by_userid(user_id=user_obj.id, db=db)
    if db_code:
        db.delete(db_code)
        db.commit()
        code = generate_code(length)
        code_obj = auth_models.VerificationCode(
            id=uuid4().hex, user_id=user_obj.id, code=code)
        db.add(code_obj)
        db.commit()
        db.refresh(code_obj)
    else:
        code = generate_code(length)
        code_obj = auth_models.VerificationCode(
            id=uuid4().hex, user_id=user_obj.id, code=code)
        db.add(code_obj)
        db.commit()
        db.refresh(code_obj)

    return {"code": code}


async def create_forgot_pasword_code(user: users_schemas.UserRecoverPassword, length: int = None):
    db = _database.SessionLocal()
    user_obj = await get_user(db, email=user.email)
    print(user_obj)
    code = ""

    db_code = db.query(auth_models.PasswordResetCode).filter(
        auth_models.PasswordResetCode.user_id == user_obj.id).first()
    if db_code:
        db.delete(db_code)
        db.commit()
        code = generate_code(length)
        code_obj = auth_models.PasswordResetCode(
            id=uuid4().hex, user_id=user_obj.id, code=code)
        db.add(code_obj)
        db.commit()
        db.refresh(code_obj)
    else:
        code = generate_code(length)
        code_obj = auth_models.PasswordResetCode(
            id=uuid4().hex, user_id=user_obj.id, code=code)
        db.add(code_obj)
        db.commit()
        db.refresh(code_obj)

    return code


async def get_token_by_userid(user_id: str, db: orm.Session):
    return db.query(auth_models.Token).filter(auth_models.Token.user_id == user_id).first()


async def generate_verification_token(user_id: str, db: orm.Session):
    payload = {'user_id': user_id}
    token = _jwt.encode(payload, JWT_SECRET, ALGORITHM)
    token_obj = auth_models.VerificationToken(
        id=uuid4().hex, user_id=user_id, token=token)
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)
    return token


async def create_verification_token(user: user_models.User):
    user_obj = users_schemas.User.from_orm(user)
    db = _database.SessionLocal()
    token = ""

    db_token = db.query(auth_models.VerificationToken).filter(
        auth_models.VerificationToken.user_id == user_obj.id).first()
    if db_token:
        validate_resp = await verify_access_token(db_token.token)
        if not validate_resp["status"]:
            db.delete(db_token)
            db.commit()
            token = await generate_verification_token(user_obj.id, db)
        else:
            token = (db_token.token)
    else:
        token = await generate_verification_token(user_obj.id, db)

    return {"token": token}


async def generate_passwordreset_token(data: dict, db: orm.Session):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=1440)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    token_obj = auth_models.PasswordResetToken(
        id=uuid4().hex, user_id=data["user_id"], token=encoded_jwt)
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)
    return encoded_jwt


async def create_passwordreset_token(user: user_models.User):
    user_obj = users_schemas.User.from_orm(user)
    db = _database.SessionLocal()
    token = ""

    db_token = db.query(auth_models.VerificationToken).filter(
        auth_models.VerificationToken.user_id == user_obj.id).first()
    if db_token:
        validate_resp = await verify_access_token(db_token.token)
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
    db_token = await get_token_by_userid(user_id=user.id, db=db)
    print(db_token)
    db.delete(db_token)
    db.commit()
    return True


async def password_change_code(password: users_schemas.UserPasswordUpdate, code: str, db: orm.Session):

    code_db = await get_password_reset_code_from_db(code, db)
    if code_db:
        user = await get_user(db=db, id=code_db.user_id)
        user.password = _hash.sha256_crypt.hash(password.password)
        db.commit()
        db.refresh(user)

        db.delete(code_db)
        db.commit()
        return {"message": "password change successful"}


async def verify_user_token(token: str):
    db = _database.SessionLocal()
    validate_resp = await verify_access_token(token)
    if not validate_resp["status"]:
        raise fastapi.HTTPException(
            status_code=401, detail=validate_resp["data"]
        )

    user = await get_user(db=db, id=validate_resp["data"]["user_id"])
    user.is_verified = True

    db.commit()
    db.refresh(user)

    return users_schemas.User.from_orm(user)


async def password_change_token(password: users_schemas.UserPasswordUpdate, token: str, db: orm.Session):
    validate_resp = await verify_access_token(token)
    if not validate_resp["status"]:
        raise fastapi.HTTPException(
            status_code=401, detail=validate_resp["data"]
        )

    token_db = db.query(auth_models.PasswordResetToken).filter(
        auth_models.PasswordResetToken.token == token).first()
    if token_db:
        user = await get_user(db=db, id=validate_resp["data"]["user_id"])
        user.password = _hash.sha256_crypt.hash(password.password)
        db.commit()
        db.refresh(user)

        db.delete(token_db)
        db.commit()
        return {"message": "password change successful"}
    else:
        raise fastapi.HTTPException(status_code=401, detail="Invalid Token")


######################### DEFAULT AUTH MAIL SERVICES #####################################


async def send_code_password_reset_email(
    email: str, db: orm.Session, codelength: int = None
):
    user = await get_user(db, email=email)
    if user:
        code = await create_forgot_pasword_code(user, codelength)
        print(code)
        await send_email_user(email, user, template='password_reset.html', title="Password Reset", code=code)
        return code
    else:
        raise fastapi.HTTPException(
            status_code=401, detail="Email not registered")


async def resend_code_verification_mail(
    email: str, db: orm.Session, codelength: int = None
):
    user = await get_user(db, email=email)
    if user:
        code = await create_verification_code(user, codelength)
        await send_email_user(email, user, template=settings.EMAIL_VERIFICATION_TEMPLATE, title="Account Verify", code=code)
        return code
    else:
        raise fastapi.HTTPException(
            status_code=401, detail="Email not registered")


async def send_token_password_reset_email(
    email: str, redirect_url: str, db: orm.Session
):
    user = await get_user(db, email=email)
    if user:
        token = await create_passwordreset_token(user)
        path = "{}/?token={}".format(redirect_url, token["token"])
        await send_email_user(email, user, template=settings.PASSWORD_RESET_TEMPLATE, title="Change Your Password", path=path)
        return {"token": token}
    else:
        raise fastapi.HTTPException(
            status_code=401, detail="Email not registered")


async def resend_token_verification_mail(
    email: str, redirect_url: str, db: orm.Session
):
    user = await get_user(db, email=email)
    if user:
        token = await create_verification_token(user)
        path = "{}/?token={}".format(redirect_url, token["token"])
        await send_email_user(email, user, template=settings.EMAIL_VERIFICATION_TEMPLATE, title="Verify Your Account", path=path)
        return {"token": token}
    else:
        raise fastapi.HTTPException(
            status_code=401, detail="Email not registered")


async def get_code_by_userid(user_id: str, db: orm.Session):
    return db.query(auth_models.VerificationCode).filter(auth_models.VerificationCode.user_id == user_id).first()


async def get_password_reset_code_from_db(code: str, db: orm.Session):
    return db.query(auth_models.PasswordResetCode).filter(auth_models.PasswordResetCode.code == code).first()


# function to get user by email or id
async def get_user(db: orm.Session, email: str = "", id: str = ""):
    response = ""
    if id != "":
        response = db.query(user_models.User).filter(
            user_models.User.id == id).first()
    if email != "":
        response = db.query(user_models.User).filter(
            user_models.User.email == email).first()

    return response
