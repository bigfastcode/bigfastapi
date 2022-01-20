from fastapi import APIRouter, Request
from typing import List
import fastapi as _fastapi
from fastapi.param_functions import Depends
import fastapi.security as _security
import sqlalchemy.orm as _orm
from . import services as _services, schema as _schemas
from fastapi import BackgroundTasks
from bigfastapi.db.database import get_db

app = APIRouter(tags=["Auth",])

@app.post("/users", status_code=201)
async def create_user(user: _schemas.UserCreate, db: _orm.Session = _fastapi.Depends(get_db)):
    verification_method = ""
    if user.verification_method.lower() != "code" and user.verification_method != "token".lower():
        raise _fastapi.HTTPException(status_code=400, detail="use a valid verification method, either code or token")
    
    verification_method = user.verification_method.lower()
    if verification_method == "token":
        if  not _services.ValidateUrl(user.verification_redirect_url):
            raise _fastapi.HTTPException(status_code=400, detail="Enter a valid redirect url")

    db_user = await _services.get_user_by_email(user.email, db)
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Email already in use")

    is_valid = _services.validate_email(user.email)
    if not is_valid["status"]:
        raise _fastapi.HTTPException(status_code=400, detail=is_valid["message"])

    userDict = await _services.create_user(verification_method, user, db)
    access_token = await _services.create_token(userDict["user"])
    return {"access_token": access_token, "verification_info": userDict["verification_info"]}


@app.post("/login")
async def login_user(
    user: _schemas.UserLogin,
    db: _orm.Session = _fastapi.Depends(get_db),
):
    user = await _services.authenticate_user(user.email, user.password, db)

    if not user:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Credentials")
    else:
        user_info = await _services.get_user_by_email(user.email, db)

        if user_info.password == "":
            raise _fastapi.HTTPException(status_code=401, detail="This account can only be logged in through social auth")
        elif not user_info.is_active:
            raise _fastapi.HTTPException(status_code=401, detail="Your account is inactive")
        elif not user_info.is_verified:
            raise _fastapi.HTTPException(status_code=401, detail="Your account is not verified")
        else:
            return await _services.create_token(user_info)



@app.post("/login/organization")
async def login_user(user: _schemas.UserOrgLogin,db: _orm.Session = _fastapi.Depends(get_db),):
    user_d = user
    user = await _services.authenticate_user(user.email, user.password, db)

    if not user:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    user_info = await _services.get_user_by_email(user.email, db)

    if not user_info.is_active:
        raise _fastapi.HTTPException(status_code=401, detail="Your account is Inactive")

    if user_info.organization == "":
        raise _fastapi.HTTPException(status_code=401, detail="You are not part of an organization")
    print(user_info.organization.lower())
    print(user.organization.lower())

    if user_info.organization.lower() != user_d.organization.lower():
        raise _fastapi.HTTPException(status_code=401, detail="You are not part of {}".format(user_d.organization))

    return await _services.create_token(user_info)


@app.post("/logout")
async def logout_user(user: _schemas.User = _fastapi.Depends(_services.is_authenticated)):
   if await _services.logout(user):
        return {"message": "logout successful"}


@app.get("/users/me", response_model=_schemas.User)
async def get_user(user: _schemas.User = _fastapi.Depends(_services.is_authenticated)):
    return user


@app.put("/users/me")
async def update_user(
    user_update: _schemas.UserUpdate,
    user: _schemas.User = _fastapi.Depends(_services.is_authenticated),
    db: _orm.Session = _fastapi.Depends(get_db),
    ):
    await _services.user_update(user_update, user, db)

# ////////////////////////////////////////////////////CODE ////////////////////////////////////////////////////////////// 
@app.post("/users/resend-verification/code")
async def resend_code_verification(
    email : _schemas.UserCodeVerification,
    db: _orm.Session = _fastapi.Depends(get_db),
    ):
    return await _services.resend_code_verification_mail(email.email, db, email.code_length)

@app.post("/users/verify/code/{code}")
async def verify_user_with_code(
    code: str,
    db: _orm.Session = _fastapi.Depends(get_db),
    ):
    return await _services.verify_user_code(code)


@app.post("/users/forgot-password/code")
async def send_code_password_reset_email(
    email : _schemas.UserCodeVerification,
    db: _orm.Session = _fastapi.Depends(get_db),
    ):
    return await _services.send_code_password_reset_email(email.email, db, email.code_length)


@app.put("/users/password-change/code/{code}")
async def password_change_with_code(
    password : _schemas.UserPasswordUpdate,
    code: str,
    db: _orm.Session = _fastapi.Depends(get_db),
    ):
    return await _services.password_change_code(password, code, db)

# ////////////////////////////////////////////////////CODE //////////////////////////////////////////////////////////////



# ////////////////////////////////////////////////////TOKEN ////////////////////////////////////////////////////////////// 
@app.post("/users/resend-verification/token")
async def resend_token_verification(
    email : _schemas.UserTokenVerification,
    db: _orm.Session = _fastapi.Depends(get_db),
    ):
    return await _services.resend_token_verification_mail(email.email, email.redirect_url, db)

@app.post("/users/verify/token/{token}")
async def verify_user_with_token(
    token: str,
    db: _orm.Session = _fastapi.Depends(get_db),
    ):
    return await _services.verify_user_token(token)


@app.post("/users/forgot-password/token")
async def send_token_password_reset_email(
    email : _schemas.UserTokenVerification,
    db: _orm.Session = _fastapi.Depends(get_db),
    ):
    return await _services.send_token_password_reset_email(email.email, email.redirect_url,db)


@app.put("/users/password-change/token/{token}")
async def password_change_with_token(
    password : _schemas.UserPasswordUpdate,
    token: str,
    db: _orm.Session = _fastapi.Depends(get_db),
    ):
    return await _services.password_change_token(password, token, db)

# ////////////////////////////////////////////////////TOKEN //////////////////////////////////////////////////////////////

async def get_user_by_email(email: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.email == email).first()

async def get_user_by_id(id: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.id == id).first()


async def create_user(verification_method: str, user: _schemas.UserCreate, db: _orm.Session):
    verification_info = ""
    user_obj = _models.User(
        id = uuid4().hex,email=user.email, password=_hash.bcrypt.hash(user.password),
        first_name=user.first_name, last_name=user.last_name,
        is_active=True, is_verified = False
    )
    db.add(user_obj)
    db.commit()
    if verification_method == "code":
        code = await resend_code_verification_mail(user_obj.email, db, user.verification_code_length)
        verification_info = code["code"]
    elif verification_method == "token":
        token = await resend_token_verification_mail(user_obj.email,user.verification_redirect_url, db)
        verification_info = token["token"]
    db.refresh(user_obj)
    return {"user":user_obj, "verification_info": verification_info}


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
