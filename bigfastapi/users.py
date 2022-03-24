from operator import inv
from re import L
from typing import Optional
from bigfastapi.schemas import store_user_schemas
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
import fastapi as fastapi
from fastapi.responses import JSONResponse
from sqlalchemy import and_
import os

import passlib.hash as _hash
from bigfastapi.models import organisation_models, user_models, auth_models
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, status
import sqlalchemy.orm as orm
from bigfastapi.db.database import get_db
from .schemas import users_schemas as _schemas
from .schemas import store_invite_schemas as _invite_schemas
from .auth_api import is_authenticated, send_code_password_reset_email,  resend_token_verification_mail, verify_user_token, password_change_token
from .files import deleteFile, isFileExist, upload_image
from .email import send_email
from .models import store_invite_model, store_user_model, role_models


app = APIRouter(tags=["User"])

# app.mount('static', StaticFiles(directory="static"), name='static')


@app.get("/users/me", response_model=_schemas.User)
async def get_user(user: _schemas.User = fastapi.Depends(is_authenticated)):
    return user


@app.put("/users/me")
async def update_user(
    user_update: _schemas.UserUpdate,
    user: _schemas.User = fastapi.Depends(is_authenticated),
    db: orm.Session = fastapi.Depends(get_db),
):
    return await user_update(user_update, user, db)


# user must be a super user to perform this
@app.put("/users/{user_id}/activate")
async def activate_user(user_activate: _schemas.UserActivate, user_id: str, user: _schemas.User = fastapi.Depends(is_authenticated),
                        db: orm.Session = fastapi.Depends(get_db)):
    if user.is_superuser == False:
        raise fastapi.HTTPException(
            status_code=403, detail="only super admins can perform this operation")
    user_act = await get_user(db, id=user_id)
    if user.is_active == True:
        raise fastapi.HTTPException(
            status_code=403, detail="this user is already active")
    await activate(user_activate, user_id, db)


@app.post("/users/recover-password")
async def recover_password(email: _schemas.UserRecoverPassword, db: orm.Session = fastapi.Depends(get_db)):
    user = await get_user(db=db, email=email.email)
    await delete_password_reset_code(db, user.id)
    await send_code_password_reset_email(email.email, db)
    return f"password reset code has been sent to {email.email}"


@app.post("/users/reset-password")
async def reset_password(user: _schemas.UserResetPassword, db: orm.Session = fastapi.Depends(get_db)):
    code_exist = await get_password_reset_code_sent_to_email(user.code, db)
    if code_exist is None:
        raise fastapi.HTTPException(status_code=403, detail="invalid code")
    return await resetpassword(user, code_exist.user_id, db)


@app.put('/users/profile/update')
async def updateUserProfile(
        payload: _schemas.UpdateUserReq,
        db: orm.Session = fastapi.Depends(get_db),
        user: str = fastapi.Depends(is_authenticated)):

    updatedUser = await updateUserDetails(db, user.id, payload)
    return {"data": updatedUser}


@app.patch('/users/password/update')
async def updatePassword(
        payload: _schemas.updatePasswordRequest,
        db: orm.Session = fastapi.Depends(get_db),
        user: str = fastapi.Depends(is_authenticated)):

    dbResponse = await updateUserPassword(db, user.id, payload)
    return {"data":  dbResponse}


@app.put('/users/accept-invite/{token}')
def accept_invite(
        payload: _invite_schemas.StoreUser,
        token: str,
        db: orm.Session = fastapi.Depends(get_db)):

    existing_invite = db.query(
        store_invite_model.StoreInvite).filter(
            and_(
                store_invite_model.StoreInvite.invite_code == token,
                store_invite_model.StoreInvite.is_deleted == False,
                store_invite_model.StoreInvite.is_revoked == False
            )).first()

    if existing_invite is None:
        return JSONResponse({
            "message": "Invite not found! Try again or ask the inviter to invite you again."
        }, status_code=404)

    existing_user = db.query(user_models.User).filter(
        user_models.User.email == existing_invite.user_email).first()

    if existing_user is None:
        return JSONResponse({
            "message": "You must log in first"
        }, status_code=403)

    # check if the invite token exists in the db.
    invite = db.query(store_invite_model.StoreInvite).filter(
        store_invite_model.StoreInvite.invite_code == token).first()
    if invite is None:
        return JSONResponse({
            "message": "Invite not found!"
        }, status_code=status.HTTP_404_NOT_FOUND)

    # TO-DO
    # check if the store user exist and update before creating store user

    # create store user
    store_user = store_user_model.StoreUser(
        store_id=payload.organization_id,
        user_id=payload.user_id,
        role_id=invite.role_id
    )
    db.add(store_user)
    db.commit()
    db.refresh(store_user)

    invite.is_deleted = True
    invite.is_accepted = True
    db.add(invite)
    db.commit()
    db.refresh(invite)

    return JSONResponse({
        "id": invite.store_id
    }, status_code=status.HTTP_200_OK)


@app.post("/users/invite/", status_code=201)
async def invite_user(
    payload: _invite_schemas.UserInvite,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "invite_email.html",
    db: orm.Session = fastapi.Depends(get_db)
):
    """
        An endpoint to invite users to a store.

        Returns dict: message 
    """

    invite_token = uuid4().hex
    invite_url = f"{payload.app_url}/accept-invite?code={invite_token}"
    payload.email_details.link = invite_url
    email_info = payload.email_details

    role = (
        db.query(role_models.Role)
        .filter(role_models.Role.role_name == payload.user_role.lower())
        .first()
        )

    # make sure you can't send invite to yourself
    invite_ctrl = (
        db.query(user_models.User)
        .filter(user_models.User.email == payload.user_email)
        .first()
    )
    if invite_ctrl is None:
        # check if user_email already exists
        existing_invite = (
            db.query(store_invite_model.StoreInvite)
            .filter(
                and_(
                    store_invite_model.StoreInvite.user_email == payload.user_email,
                    store_invite_model.StoreInvite.is_deleted == False
                )).first())
        if existing_invite is None:

            # send invite email to user
            send_email(email_details=email_info,
                       background_tasks=background_tasks, template=template, db=db)
            invite = store_invite_model.StoreInvite(
                id=uuid4().hex,
                store_id=payload.store.get("id"),
                user_id=payload.user_id,
                user_email=payload.user_email,
                role_id=role.id,
                invite_code=invite_token
            )
            db.add(invite)
            db.commit()
            db.refresh(invite)

            return {"message": "Store invite email will be sent in the background."}
        return {"message": "invite already sent"}
    return {"message": "Enter an email you're not logged in with."}


@app.get('/users/invite/{invite_code}')
async def get_single_invite(
    invite_code: str,
    db: orm.Session = fastapi.Depends(get_db),
):

    """
        Get single invite by invite code.
    """

    # user invite code to query the invite table
    existing_invite = db.query(
        store_invite_model.StoreInvite).filter(
            and_(
                store_invite_model.StoreInvite.invite_code == invite_code,
                store_invite_model.StoreInvite.is_deleted == False,
                store_invite_model.StoreInvite.is_revoked == False
            )).first()
    existing_user = db.query(user_models.User).filter(
        user_models.User.email == existing_invite.user_email).first()

    store = db.query(organisation_models.Organization).filter(
        organisation_models.Organization.id == existing_invite.store_id).first()

    # existing_invite.__setattr__('store', store)
    setattr(existing_invite, 'store', store)
    if(existing_user is not None):
        existing_user = 'exists'
    if not existing_invite:
        return JSONResponse({
            "message": "Invite not found! Try again or ask the inviter to invite you again."
        }, status_code=404)

    return {"invite": existing_invite, "user": existing_user}


@app.put("/users/invite/{invite_code}/decline")
def decline_invite(invite_code: str, db: orm.Session = fastapi.Depends(get_db)):
    """
        Decline store invite
    """

    declined_invite = (
        db.query(store_invite_model.StoreInvite)
        .filter(store_invite_model.StoreInvite.invite_code == invite_code)
        .first()
    )

    declined_invite.is_deleted = True
    db.add(declined_invite)
    db.commit()
    db.refresh(declined_invite)

    return declined_invite


@app.delete("/users/revoke-invite/{invite_code}")
def revoke_invite(
    invite_code: str,
    db: orm.Session = fastapi.Depends(get_db)
):
    """
        Revokes the invitation of a previously invited user.
    """
    revoked_invite = (
        db.query(store_invite_model.StoreInvite)
        .filter(store_invite_model.StoreInvite.invite_code == invite_code)
        .first()
    )

    revoked_invite.is_revoked = True
    revoked_invite.is_deleted = True
    db.add(revoked_invite)
    db.commit()
    db.refresh(revoked_invite)

    return revoked_invite

@app.patch("/users/{user_id}/change")
def update_user_role(
    payload: store_user_schemas.UserUpdate,
    db: orm.Session = fastapi.Depends(get_db)
):
    
    existing_user = (
        db.query(user_models.User)
        .filter(
            user_models.User.email == payload.email
        )
        .first()
    )

    if existing_user is not None:
        existing_store_user = (
            db.query(store_user_model.StoreUser)
            .filter(store_user_model.StoreUser.user_id == existing_user.id)
            .first()
        )

        # fetch the role id of payload.role from the role table
        # update the role id in existing store user to use that.
        role = (
        db.query(role_models.Role)
        .filter(role_models.Role.role_name == payload.role.lower())
        .first()
        )
        existing_store_user.role_id = role.id
        db.add(existing_store_user)
        db.commit()
        db.refresh(existing_store_user)

        return { 
            "message": "User role successfully updated", 
            "data": existing_store_user
            }
    return { "message": "User does not exist" }

# ////////////////////////////////////////////////////CODE //////////////////////////////////////////////////////////////

# @app.post("/users/verify/code/{code}")
# async def verify_user_with_code(
#     code: str,
#     db: orm.Session = fastapi.Depends(get_db),
#     ):
#     return await verify_user_code(code)


# ////////////////////////////////////////////////////CODE //////////////////////////////////////////////////////////////


# ////////////////////////////////////////////////////TOKEN //////////////////////////////////////////////////////////////
@app.post("/users/resend-verification/token")
async def resend_token_verification(
    email: _schemas.UserTokenVerification,
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
    password: _schemas.UserPasswordUpdate,
    token: str,
    db: orm.Session = fastapi.Depends(get_db),
):
    return await password_change_token(password, token, db)


@app.patch('/users/image/upload')
async def updatePassword(
        file: UploadFile = File(...),
        db: orm.Session = fastapi.Depends(get_db),
        user: str = fastapi.Depends(is_authenticated)):

    bucketName = 'profileImages'
    checkAndDeleteRes = await deleteIfFileExistPrior(user)

    uploadedImage = await upload_image(file, db, bucketName)
    imageEndpoint = constructImageEndpoint(uploadedImage, bucketName)

    updatedUser = await updateUserImage(user.id, db, imageEndpoint)
    return {"data":  updatedUser}


# ////////////////////////////////////////////////////TOKEN //////////////////////////////////////////////////////////////

async def deleteIfFileExistPrior(user: _schemas.User):
    # check if user object contains image endpoint
    if user.image is not None and len(user.image) > 17 and 'profileImages/' in user.image:
        # construct the image path from endpoint
        splitPath = user.image.split('profileImages/', 1)
        imagePath = f"\profileImages\{splitPath[1]}"
        fullStoragePath = os.path.abspath("filestorage") + imagePath
        print(f"fullpath: {fullStoragePath}")
        isProfileImageExistPrior = await isFileExist(fullStoragePath)
        # check if image exist in file prior and delete it
        if isProfileImageExistPrior:
            deleteRes = await deleteFile(fullStoragePath)
            print(f"isFileDeleted: {deleteRes}")
            return deleteRes
        else:
            print("image does not exist prior")
            return False

    else:
        print('prior image endpoint is not a valid image endpoint')
        return False


def constructImageEndpoint(Uploadedimage: str, bucketName: str):
    return f"/files/{bucketName}/{Uploadedimage}"


async def updateUserImage(userId: str, db: orm.Session, imageEndpoint: str):
    user = db.query(user_models.User).filter(
        user_models.User.id == userId).first()
    user.image = imageEndpoint
    try:
        db.commit()
        db.refresh(user)
        print('update user image successfully')
        return user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


async def get_password_reset_code_sent_to_email(code: str, db: orm.Session):
    return db.query(auth_models.PasswordResetCode).filter(auth_models.PasswordResetCode.code == code).first()


async def user_update(user_update: _schemas.UserUpdate, user: _schemas.User, db: orm.Session):
    user = await get_user(db=db, id=user.id)

    if user_update.first_name != "":
        user.first_name = user_update.first_name

    if user_update.last_name != "":
        user.last_name = user_update.last_name

    if user_update.phone_number != "":
        user.phone_number = user_update.phone_number

    db.commit()
    db.refresh(user)

    return _schemas.User.fromorm(user)


async def activate(user_activate: _schemas.UserActivate, user: _schemas.User, db: orm.Session):
    user = await get_user(db=db, id=user_activate.email)
    user_activate.is_activte = True
    db.commit()
    db.refresh(user)

    return _schemas.User.fromorm(user)


async def deactivate(user_activate: _schemas.UserActivate, user: _schemas.User, db: orm.Session):
    user = await get_user(db=db, email=user_activate.email)
    user_activate.is_active = False
    db.commit()
    db.refresh(user)
    return _schemas.User.fromorm(user)


async def resetpassword(user: _schemas.UserResetPassword, id: str, db: orm.Session):
    user_found = await get_user(db, id=id)
    user_found.password = _hash.sha256_crypt.hash(user.password)
    db.query(auth_models.PasswordResetCode).filter(
        auth_models.PasswordResetCode.user_id == user_found.id).delete()
    db.commit()
    db.refresh(user_found)
    return "password reset successful"


async def get_user(db: orm.Session, email="", id=""):
    if email != "":
        return db.query(user_models.User).filter(user_models.User.email == email).first()
    if id != "":
        return db.query(user_models.User).filter(user_models.User.id == id).first()


async def delete_password_reset_code(db: orm.Session, user_id: str):
    db.query(auth_models.PasswordResetCode).filter(
        auth_models.PasswordResetCode.user_id == user_id).delete()
    db.commit()


# Update user profile/Bio
async def updateUserDetails(db: orm.Session, userId: str, payload: _schemas.UpdateUserReq):
    user = db.query(user_models.User).filter(
        user_models.User.id == userId).first()

    user.first_name = payload.first_name
    user.last_name = payload.last_name
    user.email = payload.email
    user.country_code = payload.country_code
    user.phone_number = payload.phone_number
    user.country = payload.country

    try:
        db.commit()
        db.refresh(user)
        return user
    except:
        raise HTTPException(status_code=500, detail='Something went wrong')


# Update user profile/Bio
async def updateUserPassword(db: orm.Session, userId: str, payload: _schemas.updatePasswordRequest):
    if payload.password == payload.password_confirmation:
        user = db.query(user_models.User).filter(
            user_models.User.id == userId).first()
        user.password = _hash.sha256_crypt.hash(payload.password)

        try:
            db.commit()
            db.refresh(user)
            return user
        except:
            raise HTTPException(status_code=500, detail='Something went wrong')
    else:
        raise HTTPException(status_code=422, detail='Password does not match')
