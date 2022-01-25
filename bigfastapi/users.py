# from hashlib import _Hash
from uuid import uuid4
import fastapi as fastapi

import passlib.hash as _hash
from bigfastapi.models import user_models
from .utils import utils
from fastapi import APIRouter
import sqlalchemy.orm as orm
from bigfastapi.db.database import get_db
from .schemas import users_schemas as _schemas
from .auth import is_authenticated, create_token, logout, verify_user_code, password_change_code, verify_user_token, password_change_token
from .mail import resend_code_verification_mail, send_code_password_reset_email, resend_token_verification_mail

app = APIRouter(tags=["Auth",])

@app.post("/users", status_code=201)
async def create_user(user: _schemas.UserCreate, db: orm.Session = fastapi.Depends(get_db)):
    verification_method = ""
    if user.verification_method.lower() != "code" and user.verification_method != "token".lower():
        raise fastapi.HTTPException(status_code=400, detail="use a valid verification method, either code or token")
    
    verification_method = user.verification_method.lower()
    if verification_method == "token":
        if  not utils.ValidateUrl(user.verification_redirect_url):
            raise fastapi.HTTPException(status_code=400, detail="Enter a valid redirect url")

    db_user = await get_user_by_email(user.email, db)
    if db_user:
        raise fastapi.HTTPException(status_code=400, detail="Email already in use")

    is_valid = utils.validate_email(user.email)
    if not is_valid["status"]:
        raise fastapi.HTTPException(status_code=400, detail=is_valid["message"])

    userDict = await create_user(verification_method, user, db)
    access_token = await create_token(userDict["user"])
    return {"access_token": access_token, "verification_info": userDict["verification_info"]}


@app.post("/login")
async def login_user(
    user: _schemas.UserLogin,
    db: orm.Session = fastapi.Depends(get_db),
):
    user = await authenticate_user(user.email, user.password, db)

    if not user:
        raise fastapi.HTTPException(status_code=401, detail="Invalid Credentials")
    else:
        user_info = await get_user_by_email(user.email, db)

        if user_info.password == "":
            raise fastapi.HTTPException(status_code=401, detail="This account can only be logged in through social auth")
        elif not user_info.is_active:
            raise fastapi.HTTPException(status_code=401, detail="Your account is inactive")
        elif not user_info.is_verified:
            raise fastapi.HTTPException(status_code=401, detail="Your account is not verified")
        else:
            return await create_token(user_info)



@app.post("/login/organization")
async def login_user(user: _schemas.UserOrgLogin,db: orm.Session = fastapi.Depends(get_db),):
    user_d = user
    user = await authenticate_user(user.email, user.password, db)

    if not user:
        raise fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    user_info = await get_user_by_email(user.email, db)

    if not user_info.is_active:
        raise fastapi.HTTPException(status_code=401, detail="Your account is Inactive")

    if user_info.organization == "":
        raise fastapi.HTTPException(status_code=401, detail="You are not part of an organization")
    print(user_info.organization.lower())
    print(user.organization.lower())

    if user_info.organization.lower() != user_d.organization.lower():
        raise fastapi.HTTPException(status_code=401, detail="You are not part of {}".format(user_d.organization))

    return await create_token(user_info)


@app.post("/logout")
async def logout_user(user: _schemas.User = fastapi.Depends(is_authenticated)):
   if await logout(user):
        return {"message": "logout successful"}


@app.get("/users/me", response_model=_schemas.User)
async def get_user(user: _schemas.User = fastapi.Depends(is_authenticated)):
    return user


@app.put("/users/me")
async def update_user(
    user_update: _schemas.UserUpdate,
    user: _schemas.User = fastapi.Depends(is_authenticated),
    db: orm.Session = fastapi.Depends(get_db),
    ):
    await user_update(user_update, user, db)

# ////////////////////////////////////////////////////CODE ////////////////////////////////////////////////////////////// 
@app.post("/users/resend-verification/code")
async def resend_code_verification(
    email : _schemas.UserCodeVerification,
    db: orm.Session = fastapi.Depends(get_db),
    ):
    return await resend_code_verification_mail(email.email, db, email.code_length)

@app.post("/users/verify/code/{code}")
async def verify_user_with_code(
    code: str,
    db: orm.Session = fastapi.Depends(get_db),
    ):
    return await verify_user_code(code)


@app.post("/users/forgot-password/code")
async def send_code_password_reset_email(
    email : _schemas.UserCodeVerification,
    db: orm.Session = fastapi.Depends(get_db),
    ):
    return await send_code_password_reset_email(email.email, db, email.code_length)


@app.put("/users/password-change/code/{code}")
async def password_change_with_code(
    password : _schemas.UserPasswordUpdate,
    code: str,
    db: orm.Session = fastapi.Depends(get_db),
    ):
    return await password_change_code(password, code, db)

# ////////////////////////////////////////////////////CODE //////////////////////////////////////////////////////////////



# ////////////////////////////////////////////////////TOKEN ////////////////////////////////////////////////////////////// 
@app.post("/users/resend-verification/token")
async def resend_token_verification(
    email : _schemas.UserTokenVerification,
    db: orm.Session = fastapi.Depends(get_db),
    ):
    return await resend_token_verification_mail(email.email, email.redirect_url, db)

@app.post("/users/verify/token/{token}")
async def verify_user_with_token(
    token: str,
    db: orm.Session = fastapi.Depends(get_db),
    ):
    return await verify_user_token(token)


@app.post("/users/forgot-password/token")
async def send_token_password_reset_email(
    email : _schemas.UserTokenVerification,
    db: orm.Session = fastapi.Depends(get_db),
    ):
    return await send_token_password_reset_email(email.email, email.redirect_url,db)


@app.put("/users/password-change/token/{token}")
async def password_change_with_token(
    password : _schemas.UserPasswordUpdate,
    token: str,
    db: orm.Session = fastapi.Depends(get_db),
    ):
    return await password_change_token(password, token, db)

# ////////////////////////////////////////////////////TOKEN //////////////////////////////////////////////////////////////

async def get_user_by_email(email: str, db: orm.Session):
    return db.query(user_models.User).filter(user_models.User.email == email).first()

async def get_user_by_id(id: str, db: orm.Session):
    return db.query(user_models.User).filter(user_models.User.id == id).first()


async def create_user(verification_method: str, user: _schemas.UserCreate, db: orm.Session):
    verification_info = ""
    user_obj = user_models.User(
        id = uuid4().hex,email=user.email, password=_hash.sha256_crypt.hash(user.password),
        first_name=user.first_name, last_name=user.last_name,
        is_active=True, is_verified = True
    )
    db.add(user_obj)
    db.commit()

    # This all needs to be done async in a queue
    # if verification_method == "code":
    #     code = await resend_code_verification_mail(user_obj.email, db, user.verification_code_length)
    #     verification_info = code["code"]
    # elif verification_method == "token":
    #     token = await resend_token_verification_mail(user_obj.email,user.verification_redirect_url, db)
    #     verification_info = token["token"]

    db.refresh(user_obj)
    return {"user":user_obj, "verification_info": verification_info}


async def user_update(user_update: _schemas.UserUpdate, user:_schemas.User, db: orm.Session):
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

    return _schemas.User.fromorm(user)


async def authenticate_user(email: str, password: str, db: orm.Session):
    user = await get_user_by_email(db=db, email=email)

    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user