import datetime
import random
import string
from uuid import uuid4

import fastapi
import passlib.hash as _hash
import sqlalchemy.orm as orm
from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from getmac import get_mac_address as gma
from sqlalchemy import and_

from bigfastapi.db.database import get_db

from .models import auth_models, user_models
from .schemas import auth_schemas
from .services import email_services
from .utils import utils

app = APIRouter()


@app.get("/apiKey/{user_id}", status_code=200)
async def check_user_has_API_cred(user_id: str, db: orm.Session=Depends(get_db)):
    """Check if user has API credentials"""

    API_credentials = db.query(auth_models.APIKeys).filter(
        auth_models.APIKeys.user_id == user_id
    ).first()

    if not API_credentials:
        return JSONResponse({"message": "API Credentials not found"}, status_code=404)

    return JSONResponse({"message": "Users API Credentials exists"}, status_code=200)


@app.post("/apiKey", status_code=201)
async def generate(
    body: auth_schemas.APIKey, db: orm.Session = fastapi.Depends(get_db)
):
    ip = get_IP()

    # check if user has an api key on this ip address first
    find_user = await check_if_eligible_to_create_apikey(ip, body, db)

    if find_user == "Eligible":
        user = await check_user_exist(body, db)
        key = generate_api_key()
        app_id = generate_app_id()
        # ip_exist = await has_ip_addr_saved(ip, db)
        # if ip_exist["success"] == False:
        #     print('old id')
        #     app_id = generate_app_id()
        # else:
        #     print("existing IP")
        #     app_id = ip_exist["app_id"]

        user_id = user
        resp = await save_apikey_to_db(key, app_id, user_id, ip, db, body)

        return {"message": "success", "API_KEY": key, "APP_ID": resp.app_id}


@app.post("/get-apikey")
async def get_api_key(
    body: auth_schemas.APIKEYCheck, db: orm.Session = fastapi.Depends(get_db)
):
    user = check_api_key(body.app_id, body.api_key, db)
    return {"user": auth_schemas.UserCreateOut.from_orm(user)}


@app.post("/recover-apikey")
async def recover_apikey(
    background_tasks: BackgroundTasks,
    body: auth_schemas.APIKey,
    db: orm.Session = fastapi.Depends(get_db),
):
    user = await find_user(
        db=db,
        email=body.email,
        phone_number=body.phone_number,
        country_code=body.phone_country_code,
    )

    if not user:
        raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")

    code = ""
    if body.email != None:
        code = await send_recover_apikey_email(
            email=body.email, user=user, background_tasks=background_tasks
        )

    code_obj = auth_models.PasswordResetCode(id=uuid4().hex, user_id=user.id, code=code)

    db.add(code_obj)
    db.commit()
    db.refresh(code_obj)

    return f"Reset Code Sent To ${body.email}"


@app.post("/reset-apikey")
async def reset_apikey(
    user: auth_schemas.APIKeyReset, db: orm.Session = fastapi.Depends(get_db)
):

    code_exist = (
        db.query(auth_models.PasswordResetCode)
        .filter(auth_models.PasswordResetCode.code == user.code)
        .first()
    )
    if code_exist is None:
        raise fastapi.HTTPException(status_code=403, detail="invalid code")

    return await resetapikey(code_exist, db)


async def resetapikey(user, db: orm.Session):
    print(user.user_id)
    find_user = (
        db.query(user_models.User).filter(user_models.User.id == user.user_id).first()
    )
    print(find_user.id)
    apikey = generate_api_key()
    appid = generate_app_id()
    ip = get_IP()

    db.query(auth_models.PasswordResetCode).filter(
        auth_models.PasswordResetCode.user_id == find_user.id
    ).delete()

    db.commit()

    db.query(auth_models.APIKeys).filter(
        auth_models.APIKeys.user_id == find_user.id
    ).delete()

    db.commit()

    apikey_obj = auth_models.APIKeys(
        id=uuid4().hex,
        user_id=find_user.id,
        app_name="",
        app_id=appid,
        is_enabled=True,
        key=_hash.sha256_crypt.hash(apikey),
        ipAddr=ip,
    )

    db.add(apikey_obj)
    db.commit()
    db.refresh(apikey_obj)

    return {"message": "APIkey Reset Successful", "APIKEY": apikey, "APPID": appid}


async def send_recover_apikey_email(
    email: str, user, background_tasks: BackgroundTasks
):
    S = 7
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=S))
    template_body = {
        "body": f"Your APIKey reset code is {code}",
        "preheader": "APIKey Reset",
        "sender": "CPME",
        "title": "APIKEY RESET",
    }
    await email_services.send_email(
        background_tasks,
        recipients=[email],
        template="base_email.html",
        title="APIKey Reset",
        template_body=template_body,
    )
    return code


def check_api_key(app_id: str, api_key: str, db: orm.Session):
    get_IP()
    app = (
        db.query(auth_models.APIKeys)
        .filter(auth_models.APIKeys.app_id == app_id)
        .first()
    )

    if app != None:
        # if app.ipAddr != ip:
        #     raise fastapi.HTTPException(
        #         status_code=403, detail="Invalid IP Address")

        veri = app.verify_apikey(api_key)
        if not veri:
            raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")

        user = (
            db.query(user_models.User)
            .filter(user_models.User.id == app.user_id)
            .first()
        )
        return user
    else:
        raise fastapi.HTTPException(status_code=403, detail="Invalid Credentials")


async def save_apikey_to_db(
    key, app_id, user_id, ip, db: orm.Session, body: auth_schemas.APIKey = ""
):
    client_id = ""
    app_name = ""
    if body != "":
        app_name = body.app_name
        client_id = body.user_id if body.user_id != None else user_id
    apikey_obj = auth_models.APIKeys(
        id=uuid4().hex,
        user_id=client_id,
        app_name=app_name,
        app_id=app_id,
        is_enabled=True,
        key=_hash.sha256_crypt.hash(key),
        ipAddr=ip,
    )

    db.add(apikey_obj)
    db.commit()
    db.refresh(apikey_obj)
    return apikey_obj


async def get_key(key, db: orm.Session):
    key = db.query(auth_models.APIKeys).filter(auth_models.APIKeys.key == key).first()
    return key


async def create_user(user: auth_schemas.APIKey, db: orm.Session):

    password = generate_app_id()
    user_obj = user_models.User(
        id=uuid4().hex,
        email=user.email,
        password_hash=_hash.sha256_crypt.hash(password),
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        is_active=True,
        is_verified=True,
        phone_country_code=user.phone_country_code,
        is_deleted=False,
        google_id=None,
        google_image_url=None,
        image_url=None,
        device_id=None,
    )

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


def get_IP():
    mac_address = gma()
    print(mac_address)
    return mac_address


def generate_api_key():
    api_key = uuid4().hex + str(datetime.datetime.now())
    key = api_key.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")
    return key


def generate_app_id():
    S = 15
    ran = "".join(random.choices(string.ascii_uppercase + string.digits, k=S))
    app_id = str(ran)
    return app_id


# this function is to check if the request to the api is coming from a device IP which has already been saved


async def has_ip_addr_saved(ip: str, db: orm.Session):
    ip_addr = (
        db.query(auth_models.APIKeys).filter(auth_models.APIKeys.ipAddr == ip).first()
    )
    # if ip address exists in the db return true and its app_id
    if ip_addr:
        return {"success": True, "app_id": ip_addr.app_id}
    else:
        return {"success": False, "app_id": "None"}


async def find_user(
    db: orm.Session, email: str = "", phone_number: str = "", country_code: str = ""
):
    if email != "":
        return (
            db.query(user_models.User).filter(user_models.User.email == email).first()
        )
    if phone_number != "" and country_code != "":
        return (
            db.query(user_models.User)
            .filter(
                and_(
                    user_models.User.phone_number == phone_number,
                    user_models.User.phone_country_code == country_code,
                )
            )
            .first()
        )
    if phone_number != "" and country_code != "" and email != "":
        return (
            db.query(user_models.User)
            .filter(
                and_(
                    user_models.User.phone_number == phone_number,
                    user_models.User.phone_country_code == country_code,
                    user_models.User.email == email,
                )
            )
            .first()
        )


async def check_if_eligible_to_create_apikey(
    ip: str, body: auth_schemas.APIKey, db: orm.Session
):
    if body.email != None:
        user = await find_user(db, body.email)

        if not user:
            return "Eligible"

        check_user = (
            db.query(auth_models.APIKeys)
            .filter(auth_models.APIKeys.user_id == user.id)
            .first()
        )

        if not check_user:
            return "Eligible"
        else:
            raise fastapi.HTTPException(
                status_code=403, detail="You already have an API key"
            )

    if body.phone_number != None and body.phone_country_code != None:
        user = await find_user(db, body.phone_number, body.phone_country_code)

        if not user:
            return "Eligible"

        check_user = (
            db.query(auth_models.APIKeys)
            .filter(auth_models.APIKeys.user_id == user.id)
            .first()
        )

        if not check_user:
            return "Eligible"
        else:
            raise fastapi.HTTPException(
                status_code=403, detail="You already have an API key"
            )

    if (
        body.phone_number != None
        and body.phone_country_code != None
        and body.email != None
    ):
        user = await find_user(
            db, body.email, body.phone_number, body.phone_country_code
        )

        if not user:
            return "Eligible"

        check_user = (
            db.query(auth_models.APIKeys)
            .filter(auth_models.APIKeys.user_id == user.id)
            .first()
        )

        if not check_user:
            return "Eligible"
        else:
            raise fastapi.HTTPException(
                status_code=403, detail="You already have an API key"
            )


async def check_user_exist(body: auth_schemas.APIKey, db: orm.Session):
    if body.user_id != None:
        user = (
            db.query(user_models.User)
            .filter(user_models.User.id == body.user_id)
            .first()
        )
        if user == None:
            raise fastapi.HTTPException(status_code=403, detail="Invalid user ID")
        return user.id

    else:
        if body.email == None and body.phone_number == None:
            raise fastapi.HTTPException(
                status_code=403,
                detail="you must use a either phone_number or email to get API key",
            )
        if body.phone_number and body.phone_country_code == None:
            raise fastapi.HTTPException(
                status_code=403,
                detail="you must add a country code when you add a phone number",
            )
        if body.phone_number and body.phone_country_code:
            check_contry_code = utils.validate_phone_dialcode(body.phone_country_code)
            if check_contry_code is None:
                raise fastapi.HTTPException(
                    status_code=403, detail="this country code is invalid"
                )
        if body.phone_number == None and body.phone_country_code:
            raise fastapi.HTTPException(
                status_code=403,
                detail="you must add a phone number when you add a country code",
            )

        # user_exist = db.query(user_models.User).filter(or_(user_models.User.email == body.email, and_(
        #     user_models.User.phone_number == body.phone_number, user_models.User.country_code == body.country_code))).first()

        user_exist = ""
        if body.email != None:
            user_exist = (
                db.query(user_models.User)
                .filter(user_models.User.email == body.email)
                .first()
            )

        if body.phone_number != None:
            user_exist = (
                db.query(user_models.User)
                .filter(
                    and_(
                        user_models.User.phone_number == body.phone_number,
                        user_models.User.phone_country_code == body.phone_country_code,
                    )
                )
                .first()
            )

        if user_exist != None:
            print(user_exist.id)
            return user_exist.id
        else:
            user = await create_user(body, db)
            return user.id
