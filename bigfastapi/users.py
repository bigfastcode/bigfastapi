from uuid import uuid4
import fastapi as fastapi

import passlib.hash as _hash
from bigfastapi.models import user_models, auth_models
from .utils import utils
from fastapi import APIRouter
import sqlalchemy.orm as orm
from bigfastapi.db.database import get_db
from .schemas import users_schemas as _schemas


from .email import send_reset_password_email

from .auth import is_authenticated, logout, create_access_token, password_change_code, verify_user_token, password_change_token, resend_code_verification_mail, send_code_password_reset_email, resend_token_verification_mail


app = APIRouter(tags=["User",])



@app.get("/users/me", response_model=_schemas.User)
async def get_user(user: _schemas.UserCreate = fastapi.Depends(is_authenticated)):
    return user


@app.put("/users/me")
async def update_user(
    user_update: _schemas.UserUpdate,
    user: _schemas.User = fastapi.Depends(is_authenticated),
    db: orm.Session = fastapi.Depends(get_db),
    ):
    return await user_update(user_update, user, db)


#user must be a super user to perform this
@app.put("/users/{user_id}/activate")
async def activate_user(user_activate: _schemas.UserActivate, user_id: str, user: _schemas.User = fastapi.Depends(is_authenticated),
    db: orm.Session = fastapi.Depends(get_db)):
    if user.is_superuser == False:
        raise _fastapi.HTTPException(status_code=403, detail="only super admins can perform this operation")
    user_act = await get_user_by_id(user_id, db)
    if user.is_active == True:
        raise _fastapi.HTTPException(status_code=403, detail="this user is already active")
    await activate(user_activate, user_id, db)
    

@app.post("/users/recover-password")
async def recover_password(email: _schemas.UserRecoverPassword, db: orm.Session = fastapi.Depends(get_db)):
    return await send_code_password_reset_email(email.email, db)


@app.put("/users/reset-password")
async def reset_password(user: _schemas.UserResetPassword, db: orm.Session = fastapi.Depends(get_db)):
    code_exist = await get_password_reset_code_sent_to_email(user.code, db)
    if code_exist is None:
        raise fastapi.HTTPException(status_code=403, detail="invalid code")
    return await resetpassword(user, db)


# ////////////////////////////////////////////////////CODE ////////////////////////////////////////////////////////////// 

@app.post("/users/verify/code/{code}")
async def verify_user_with_code(
    code: str,
    db: orm.Session = fastapi.Depends(get_db),
    ):
    return await verify_user_code(code)



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


@app.put("/users/password-change/token/{token}")
async def password_change_with_token(
    password : _schemas.UserPasswordUpdate,
    token: str,
    db: orm.Session = fastapi.Depends(get_db),
    ):
    return await password_change_token(password, token, db)

# ////////////////////////////////////////////////////TOKEN //////////////////////////////////////////////////////////////

async def get_password_reset_code_sent_to_email(code: str, db: orm.Session):
    return db.query(auth_models.PasswordResetCode).filter(auth_models.PasswordResetCode.code == code).first()


async def get_user_by_email(email: str, db: orm.Session):
    return db.query(user_models.User).filter(user_models.User.email == email).first()


async def get_user_by_id(id: str, db: orm.Session):
    return db.query(user_models.User).filter(user_models.User.id == id).first()


async def user_update(user_update: _schemas.UserUpdate, user:_schemas.User, db: orm.Session):
    user = await get_user_by_id(id = user.id, db=db)

    if user_update.first_name != "":
        user.first_name = user_update.first_name

    if user_update.last_name != "":
        user.last_name = user_update.last_name

    if user_update.phone_number != "":
        user.phone_number = user_update.phone_number
    

    db.commit()
    db.refresh(user)

    return _schemas.User.fromorm(user)


async def activate(user_activate: _schemas.UserActivate, user:_schemas.User, db: orm.Session):
    user = await get_user_by_email(id = user_activate.email, db=db)

    user_activate.is_activte = True
    
    db.commit()
    db.refresh(user)

    return _schemas.User.fromorm(user)


async def deactivate(user_activate: _schemas.UserActivate, user:_schemas.User, db: orm.Session):
    user = await get_user_by_email(email = user_activate.email, db=db)

    user_activate.is_active = False
    
    db.commit()
    db.refresh(user)

    return _schemas.User.fromorm(user)


async def resetpassword(user: _schemas.UserResetPassword, db: orm.Session):
    user_found = await get_user_by_email(email = user.email, db=db)
    user_found.password = _hash.sha256_crypt.hash(user.password)
    find_token = db.query(auth_models.Token).filter(auth_models.Token.user_id == user_found.id).all()
    db.commit()
    db.refresh(user_found)
    return "password reset successful"
