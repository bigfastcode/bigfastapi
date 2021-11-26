from fastapi import APIRouter, Request
from typing import List
import fastapi as _fastapi
from fastapi.param_functions import Depends
import fastapi.security as _security
import sqlalchemy.orm as _orm
from . import services as _services, schema as _schemas
from fastapi import BackgroundTasks
from BigFastAPI.database import get_db

app = APIRouter(tags=["Auth",])

@app.post("/users", status_code=201)
async def create_user(user: _schemas.UserCreate, db: _orm.Session = _fastapi.Depends(get_db)):
    db_user = await _services.get_user_by_email(user.email, db)
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Email already in use")

    is_valid = _services.validate_email(user.email)
    if not is_valid["status"]:
        raise _fastapi.HTTPException(status_code=400, detail=is_valid["message"])

    user = await _services.create_user(user, db)
    access_token = await _services.create_token(user)
    verification_token = await _services.create_verification_token(user)
    return {"access_token": access_token, "verification_token": verification_token}


@app.post("/login")
async def login_user(
    user: _schemas.UserLogin,
    db: _orm.Session = _fastapi.Depends(get_db),
):
    user = await _services.authenticate_user(user.email, user.password, db)

    if not user:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    user_info = await _services.get_user_by_email(user.email, db)

    if not user_info.is_active:
        raise _fastapi.HTTPException(status_code=401, detail="Your account is inactive")

    if not user_info.password == "":
        raise _fastapi.HTTPException(status_code=401, detail="This account can only be logged in through social auth")

    if not user_info.is_verified:
        raise _fastapi.HTTPException(status_code=401, detail="Your account is not verified")



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


@app.post("/users/resend-verification")
async def resend_verification(
    email : _schemas.UserVerification,
    db: _orm.Session = _fastapi.Depends(get_db),
    ):
    return await _services.resend_verification_mail(email.email, db)

@app.post("/users/verify/{token}")
async def verify_user(
    token: str,
    db: _orm.Session = _fastapi.Depends(get_db),
    ):
    return await _services.verify_user(token)


@app.post("/users/forgot-password")
async def send_password_rest_email(
    email : _schemas.UserVerification,
    db: _orm.Session = _fastapi.Depends(get_db),
    ):
    return await _services.send_password_reset_email(email.email,db)


@app.put("/users/password-change/{token}")
async def password_change(
    password : _schemas.UserPasswordUpdate,
    token: str,
    db: _orm.Session = _fastapi.Depends(get_db),
    ):
    return await _services.password_change(password, token, db)

