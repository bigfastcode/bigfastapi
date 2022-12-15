import os
from datetime import datetime

import fastapi
import passlib.hash as _hash
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from sqlalchemy import orm

from bigfastapi.db.database import get_db
from bigfastapi.models import auth_models, user_models
from bigfastapi.services.auth_service import (
    is_authenticated,
    password_change_token,
    resend_token_verification_mail,
    send_code_password_reset_email,
    verify_user_token,
)

from .files import deleteFile, is_file_exist, upload_image
from .schemas import users_schemas as _schemas

app = APIRouter(tags=["User"])


@app.get("/users/me", response_model=_schemas.User)
async def get_user(user: _schemas.User = fastapi.Depends(is_authenticated)):
    """intro-->This endpoint allows you to retrieve details about the currently logged in user, to use this endpoint you need to make a get request to the  /users/me endpoint

    returnDesc-->On sucessful request, it returns:

        returnBody--> details of the currently logged in user
    """
    return user


@app.put("/users/me")
async def update_user(
    user_update: _schemas.UserUpdate,
    user: _schemas.User = fastapi.Depends(is_authenticated),
    db: orm.Session = fastapi.Depends(get_db),
):
    """intro-->This endpoint allows you to update details about the currently logged in user, to use this endpoint you need to make a put request to the  /users/me endpoint with a specified body of request

    returnDesc-->On sucessful request, it returns:

        returnBody--> updated details of the currently logged in user
    """
    return await user_update(user_update, user, db)


# user must be a super user to perform this
@app.put("/users/{user_id}/activate")
async def activate_user(
    user_activate: _schemas.UserActivate,
    user_id: str,
    user: _schemas.User = fastapi.Depends(is_authenticated),
    db: orm.Session = fastapi.Depends(get_db),
):
    """intro-->This endpoint allows a super user to activate a user, to use this endpoint user must be a super user. You need to make a put request to the  /users/{user_id}/activate endpoint with a specified body of request to activate a user

    paramDesc--> On put request the url takes a query parameter "user_id"
        param-->notification_id: This is the unique identifier of the user
        reqBody-->email: This is the email address of the user
        reqBody-->is_active: This is the current state of user, this is set to true when the user is active and false otherwise.

    returnDesc-->On sucessful request, it returns:
        returnBody--> "success".
    """
    if user.is_superuser is False:
        raise fastapi.HTTPException(
            status_code=403, detail="only super admins can perform this operation"
        )
    existing_user = await get_user(db, id=user_id)
    if existing_user.is_active is True:
        raise fastapi.HTTPException(
            status_code=403, detail="this user is already active"
        )
    await activate(user_activate, user_id, db)


@app.post("/users/recover-password")
async def recover_password(
    email: _schemas.UserRecoverPassword,
    background_tasks: BackgroundTasks,
    db: orm.Session = fastapi.Depends(get_db),
):
    """intro-->This endpoint allows for password recovery, to use this endpoint you need to make a post request to the /users/recover-password endpoint

        reqBody-->email: This is the email address of the user

    returnDesc--> On sucessful request, it returns:
        returnBody--> "success".
    """
    user = await get_user(db=db, email=email.email)
    await delete_password_reset_code(db, user.id)
    await send_code_password_reset_email(
        email=email.email, background_tasks=background_tasks, db=db
    )
    return f"password reset code has been sent to {email.email}"


@app.post("/users/reset-password")
async def reset_password(
    user: _schemas.UserResetPassword, db: orm.Session = fastapi.Depends(get_db)
):
    """intro-->This endpoint allows a user to reset their password after recieving a given code on password recovery, to use this endpoint you need to make a post request to the /users/reset-password endpoint

        reqBody-->email: This is the email address of the user
        reqBody-->code: This is a unique code sent to the user on password recovery
        reqBody-->password: This is the registered password of the user

    returnDesc--> On sucessful request, it returns message,
        returnBody--> "success".
    """
    code_exist = await get_password_reset_code_sent_to_email(user.code, db)
    valid_time_in_secs = 1800

    if code_exist is None:
        raise fastapi.HTTPException(status_code=403, detail="invalid code")

    time_diff_in_secs = (datetime.utcnow() - code_exist.date_created).total_seconds()

    if valid_time_in_secs < time_diff_in_secs:
        raise fastapi.HTTPException(status_code=403, detail="code expired")

    return await resetpassword(user, code_exist.user_id, db)


@app.put("/users/profile/update")
async def updateUserProfile(
    payload: _schemas.UpdateUserReq,
    db: orm.Session = fastapi.Depends(get_db),
    user: str = fastapi.Depends(is_authenticated),
):
    """intro-->This endpoint allows for users to update their profile details. To use this endpoint you need to make a put request to the /users/profile/update enpoint with a specified body of request with details to be updated

        reqBody-->email: This is the email address of the user
        reqBody-->first_name: This is a unique code sent to the user on password recovery
        reqBody-->last_name: This is the registered password of the user
        reqBody-->country_code: This is the registered password of the user
        reqBody-->phone_number: This is the registered password of the user
        reqBody-->country: This is the registered password of the user
        reqBody-->state: This is the registered password of the user


    returnDesc--> On sucessful request, it returns message:

        returnBody--> "updated User".
    """

    updatedUser = await updateUserDetails(db, user.id, payload)
    return {"data": updatedUser}


@app.patch("/users/password/update")
async def updatePassword(
    payload: _schemas.updatePasswordRequest,
    db: orm.Session = fastapi.Depends(get_db),
    user: str = fastapi.Depends(is_authenticated),
):
    """intro-->This endpoint allows for users to update their password. To use this endpoint you need to make a patch request to the /users/password/update endpoint with a body of request with details of the new password.

        reqBody-->email: This is the email address of the user
        reqBody-->first_name: This is a unique code sent to the user on password recovery
        reqBody-->last_name: This is the registered password of the user
        reqBody-->country_code: This is the registered password of the user
        reqBody-->phone_number: This is the registered password of the user
        reqBody-->country: This is the registered password of the user
        reqBody-->state: This is the registered password of the user


    returnDesc--> On sucessful request, it returns message:

        returnBody--> "the User".
    """

    dbResponse = await updateUserPassword(db, user.id, payload)
    return {"data": dbResponse}


@app.post("/users/resend-verification/token")
async def resend_token_verification(
    email: _schemas.UserTokenVerification,
    db: orm.Session = fastapi.Depends(get_db),
):
    """intro--> This endpoint is used to trigger a resend of a user's verification token. To use this endpoint you need to make a post request to the /users/resend-verification/token endpoint

    paramDesc--> On post request, the url takes a user's id
        param--> user_id: This is the user id of the user
        reqBody--> email: This is the user email where the verification token will be sent to
        reqBody--> redirect_url: This is the url the user will be redirected to after verification

    returnDesc--> On sucessful request, it returns message:

        returnBody--> "success"
    """
    return await resend_token_verification_mail(email.email, email.redirect_url, db)


@app.post("/users/verify/token/{token}")
async def verify_user_with_token(
    token: str,
    db: orm.Session = fastapi.Depends(get_db),
):
    """intro-->This endpoint is used verify a user on api request. To use this endpoint you need to make a post request to the /users/verify/token/{token} endpoint

    paramDesc-->On post request, the url takes the verification token
        param-->token: This is the token sent to the user's email

    returnDesc--> On sucessful request, it returns message:

        returnBody--> "success"
    """
    return await verify_user_token(token)


@app.put("/users/password-change/token/{token}")
async def password_change_with_token(
    password: _schemas.UserPasswordUpdate,
    token: str,
    db: orm.Session = fastapi.Depends(get_db),
):
    """intro-->This endpoint is used to change a user's password. To use this endpoint you need to make a put request to the /users/password-change/token/{token} endpoint with a specified body of request

    paramDesc-->On post request, the url takes the verification token
        param-->token: This is the token sent to the user's email
        reqBody-->code: This code sent to the user's email
        reqBody-->password: This is the new user of the password

    returnDesc--> On sucessful request, it returns message:
        returnBody--> "success"
    """
    return await password_change_token(password, token, db)


@app.patch("/users/image/upload")
async def updatePassword(
    file: UploadFile = File(...),
    db: orm.Session = fastapi.Depends(get_db),
    user: str = fastapi.Depends(is_authenticated),
):

    """intro-->This endpoint is used to update a user's image.
       To use this endpoint you need to make a patch request to the /users/image/upload endpoint
       with the image file as payload and the user authorization/bearer token


    returnDesc--> On sucessful request, it returns the updated user
        returnBody--> "Updated User Object"
    """

    bucketName = "profileImages"
    # Delete prev usuer image if exist
    await deleteIfFileExistPrior(user)

    uploadedImage = await upload_image(file, db, bucketName)
    imageEndpoint = constructImageEndpoint(uploadedImage, bucketName)

    updatedUser = await updateUserImage(user.id, db, imageEndpoint)
    return {"data": updatedUser}


# ////////////////////////////////////////////////////TOKEN //////////////////////////////////////////////////////////////


async def deleteIfFileExistPrior(user: _schemas.User):
    # check if user object contains image endpoint
    if (
        user.image_url is not None
        and len(user.image_url) > 17
        and "profileImages/" in user.image_url
    ):
        # construct the image path from endpoint
        splitPath = user.image_url.split("profileImages/", 1)
        imagePath = rf"\profileImages\{splitPath[1]}"
        fullStoragePath = os.path.abspath("filestorage") + imagePath

        isProfileImageExistPrior = await is_file_exist(fullStoragePath)
        # check if image exist in file prior and delete it
        if isProfileImageExistPrior:
            deleteRes = await deleteFile(fullStoragePath)
            return deleteRes
        else:
            return False
    else:
        return False


def constructImageEndpoint(Uploadedimage: str, bucketName: str):
    return f"/files/image/{bucketName}/{Uploadedimage}"


async def updateUserImage(userId: str, db: orm.Session, imageEndpoint: str):
    user = db.query(user_models.User).filter(user_models.User.id == userId).first()
    user.image_url = imageEndpoint
    try:
        db.commit()
        db.refresh(user)
        print("update user image successfully")
        return user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


async def get_password_reset_code_sent_to_email(code: str, db: orm.Session):
    return (
        db.query(auth_models.PasswordResetCode)
        .filter(auth_models.PasswordResetCode.code == code)
        .first()
    )


async def user_update(
    user_update: _schemas.UserUpdate, user: _schemas.User, db: orm.Session
):
    user = await get_user(db=db, id=user.id)

    if user_update.first_name != "":
        user.first_name = user_update.first_name

    if user_update.last_name != "":
        user.last_name = user_update.last_name

    if user_update.phone_number != "":
        user.phone_number = user_update.phone_number

    db.commit()
    db.refresh(user)

    return _schemas.User.from_orm(user)


async def activate(
    user_activate: _schemas.UserActivate, user: _schemas.User, db: orm.Session
):
    user = await get_user(db=db, id=user_activate.email)
    user_activate.is_activte = True
    db.commit()
    db.refresh(user)

    return _schemas.User.from_orm(user)


async def deactivate(
    user_activate: _schemas.UserActivate, user: _schemas.User, db: orm.Session
):
    user = await get_user(db=db, email=user_activate.email)
    user_activate.is_active = False
    db.commit()
    db.refresh(user)
    return _schemas.User.from_orm(user)


async def resetpassword(user: _schemas.UserResetPassword, id: str, db: orm.Session):
    user_found = await get_user(db, id=id)
    user_found.password_hash = _hash.sha256_crypt.hash(user.password)
    db.query(auth_models.PasswordResetCode).filter(
        auth_models.PasswordResetCode.user_id == user_found.id
    ).delete()
    db.commit()
    db.refresh(user_found)
    return "password reset successful"


async def get_user(db: orm.Session, email="", id=""):
    if email != "":
        return (
            db.query(user_models.User).filter(user_models.User.email == email).first()
        )
    if id != "":
        return db.query(user_models.User).filter(user_models.User.id == id).first()


async def delete_password_reset_code(db: orm.Session, user_id: str):
    db.query(auth_models.PasswordResetCode).filter(
        auth_models.PasswordResetCode.user_id == user_id
    ).delete()
    db.commit()


# Update user profile/Bio
async def updateUserDetails(
    db: orm.Session, userId: str, payload: _schemas.UpdateUserReq
):
    user = db.query(user_models.User).filter(user_models.User.id == userId).first()

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
        raise HTTPException(status_code=500, detail="Something went wrong")


# Update user profile/Bio
async def updateUserPassword(
    db: orm.Session, userId: str, payload: _schemas.updatePasswordRequest
):
    if payload.password == payload.password_confirmation:
        user = db.query(user_models.User).filter(user_models.User.id == userId).first()
        user.password = _hash.sha256_crypt.hash(payload.password)

        try:
            db.commit()
            db.refresh(user)
            return user
        except:
            raise HTTPException(status_code=500, detail="Something went wrong")
    else:
        raise HTTPException(status_code=422, detail="Password does not match")
