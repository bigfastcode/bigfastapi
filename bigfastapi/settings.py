
from uuid import uuid4
from fastapi import APIRouter, Request
from typing import List
import fastapi as fastapi
from fastapi.param_functions import Depends
import fastapi.security as _security
from sqlalchemy import schema
import sqlalchemy.orm as _orm
from .schemas import organisation_schemas as _schemas
from .schemas import users_schemas
from bigfastapi.db.database import get_db
from .auth import is_authenticated
from .models import organisation_models as _models
import datetime as _dt



from .schemas import settings_schemas as schemas 
from .schemas import users_schemas
from .auth import is_authenticated
from .models import settings_models as models
import datetime as _dt



# from uuid import uuid4
# import fastapi as fastapi

# import passlib.hash as _hash
# from bigfastapi.models import user_models
# from .utils import utils
# from fastapi import APIRouter
# import sqlalchemy.orm as orm
# from bigfastapi.db.database import get_db
# from .schemas import users_schemas as _schemas
# from .auth import is_authenticated, create_token, logout, verify_user_code, password_change_code, verify_user_token, password_change_token
# from .mail import resend_code_verification_mail, send_code_password_reset_email, resend_token_verification_mail


app = APIRouter(tags=["Settings"])



@app.get("/settings/{organisation_id}" )
async def root():
    return {"message": "Hello World"}



@app.get("/settings/{settings_name}")
async def get_settings(settings_name: str, query):
    return {
        "Name": "John",
        "Age": 30,
        "query": query,
    }


@app.post("/settings/post")
async def post_settings(name_value: schemas.Settings):
    print(name_value)
    return {
        "name": name_value.name
    }




# async def get_settings(settings: str = "", db: _orm.Session = Depends(get_db)):
#     settings_info = await models.Settings.get_settings(settings, db)
#     return settings_info


# @app.get("/settings/organizations/{settings_name}", )
# async def get_settings( settings_name: str, db: _orm.Session, request: Request, ):
#     settings = db.query(_models.Settings).filter(_models.Settings.name == settings_name).first()
#     if settings is None:
#         raise fastapi.HTTPException(status_code=404, detail="Settings does not exist")
#     return _schemas.Settings.from_orm(settings)





# @app.get("settings/organizations", response_model=List[schemas.Settings], status_code=200)
# async def get_settings(
#     user: users_schemas.User = fastapi.Depends(is_authenticated),
#     db: _orm.Session = fastapi.Depends(get_db),
# ):
#     return await get_settings(user=user, db=db)



# @app.post("settings/organizations", response_model=_schemas.Organization)
# async def get_settings(
#     organization: _schemas.OrganizationCreate,
#     user: users_schemas.User = _fastapi.Depends(is_authenticated),
#     db: _orm.Session = _fastapi.Depends(get_db),
# ):
#     db_org = await get_orgnanization_by_name(name = organization.name, db=db)
#     print(db_org)
#     if db_org:
#         raise _fastapi.HTTPException(status_code=400, detail="Organization name already in use")
#     return await create_organization(user=user, db=db, organization=organization)





# @app.get("/organizations/{organization_id}", status_code=200)
# async def get_organization(
#     organization_id: int,
#     user: users_schemas.User = _fastapi.Depends(is_authenticated),
#     db: _orm.Session = _fastapi.Depends(get_db),
# ):
#     return await get_organization(organization_id, user, db)










































# # /////////////////////////////////////////////////////////////////////////////////
# # Organisation Services

# async def get_orgnanization_by_name(name: str, db: _orm.Session):
#     return db.query(_models.Organization).filter(_models.Organization.name == name).first()



# async def create_organization(user: users_schemas.User, db: _orm.Session, organization: _schemas.OrganizationCreate):
#     organization = _models.Organization(id=uuid4().hex, creator=user.id, mission= organization.mission, 
#     vision= organization.vision, values= organization.values, name= organization.name)
#     db.add(organization)
#     db.commit()
#     db.refresh(organization)
#     return _schemas.Organization.from_orm(organization)


# async def get_organizations(user: users_schemas.User, db: _orm.Session):
#     organizations = db.query(_models.Organization).filter_by(owner_id=user.id)

#     return list(map(_schemas.Organization.from_orm, organizations))


# async def _organization_selector(organization_id: int, user: users_schemas.User, db: _orm.Session):
#     organization = (
#         db.query(_models.Organization)
#         .filter_by(creator=user.id)
#         .filter(_models.Organization.id == organization_id)
#         .first()
#     )

#     if organization is None:
#         raise _fastapi.HTTPException(status_code=404, detail="Organization does not exist")

#     return organization


# async def get_organization(organization_id: int, user: users_schemas.User, db: _orm.Session):
#     organization = await _organization_selector(organization_id=organization_id, user=user, db=db)

#     return _schemas.Organization.from_orm(organization)


# async def delete_organization(organization_id: int, user: users_schemas.User, db: _orm.Session):
#     organization = await _organization_selector(organization_id, user, db)

#     db.delete(organization)
#     db.commit()

# async def update_organization(organization_id: int, organization: _schemas.OrganizationUpdate, user: users_schemas.User, db: _orm.Session):
#     organization_db = await _organization_selector(organization_id, user, db)

#     if organization.mission != "":
#         organization_db.mission = organization.mission

#     if organization.vision != "":
#         organization_db.vision = organization.vision

#     if organization.values != "":
#         organization_db.values = organization.values

#     if organization.name != "":
#         db_org = await get_orgnanization_by_name(name = organization.name, db=db)
#         if db_org:
#             raise _fastapi.HTTPException(status_code=400, detail="Organization name already in use")
#         else:
#             organization_db.name = organization.name       

#     organization_db.last_updated = _dt.datetime.utcnow()

#     db.commit()
#     db.refresh(organization_db)

#     return _schemas.Organization.from_orm(organization_db)





























# ### USERS


# # from hashlib import _Hash
# from uuid import uuid4
# import fastapi as fastapi

# import passlib.hash as _hash
# from bigfastapi.models import user_models
# from .utils import utils
# from fastapi import APIRouter
# import sqlalchemy.orm as orm
# from bigfastapi.db.database import get_db
# from .schemas import users_schemas as _schemas
# from .auth import is_authenticated, create_token, logout, verify_user_code, password_change_code, verify_user_token, password_change_token
# from .mail import resend_code_verification_mail, send_code_password_reset_email, resend_token_verification_mail

# app = APIRouter(tags=["Auth",])

# @app.post("/users", status_code=201)
# async def create_user(user: _schemas.UserCreate, db: orm.Session = fastapi.Depends(get_db)):
#     verification_method = ""
#     if user.verification_method.lower() != "code" and user.verification_method != "token".lower():
#         raise fastapi.HTTPException(status_code=400, detail="use a valid verification method, either code or token")
    
#     verification_method = user.verification_method.lower()
#     if verification_method == "token":
#         if  not utils.ValidateUrl(user.verification_redirect_url):
#             raise fastapi.HTTPException(status_code=400, detail="Enter a valid redirect url")

#     db_user = await get_user_by_email(user.email, db)
#     if db_user:
#         raise fastapi.HTTPException(status_code=400, detail="Email already in use")

#     is_valid = utils.validate_email(user.email)
#     if not is_valid["status"]:
#         raise fastapi.HTTPException(status_code=400, detail=is_valid["message"])

#     userDict = await create_user(verification_method, user, db)
#     access_token = await create_token(userDict["user"])
#     return {"access_token": access_token, "verification_info": userDict["verification_info"]}


# @app.post("/login")
# async def login_user(
#     user: _schemas.UserLogin,
#     db: orm.Session = fastapi.Depends(get_db),
# ):
#     user = await authenticate_user(user.email, user.password, db)

#     if not user:
#         raise fastapi.HTTPException(status_code=401, detail="Invalid Credentials")
#     else:
#         user_info = await get_user_by_email(user.email, db)

#         if user_info.password == "":
#             raise fastapi.HTTPException(status_code=401, detail="This account can only be logged in through social auth")
#         elif not user_info.is_active:
#             raise fastapi.HTTPException(status_code=401, detail="Your account is inactive")
#         elif not user_info.is_verified:
#             raise fastapi.HTTPException(status_code=401, detail="Your account is not verified")
#         else:
#             return await create_token(user_info)



# @app.post("/login/organization")
# async def login_user(user: _schemas.UserOrgLogin,db: orm.Session = fastapi.Depends(get_db),):
#     user_d = user
#     user = await authenticate_user(user.email, user.password, db)

#     if not user:
#         raise fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

#     user_info = await get_user_by_email(user.email, db)

#     if not user_info.is_active:
#         raise fastapi.HTTPException(status_code=401, detail="Your account is Inactive")

#     if user_info.organization == "":
#         raise fastapi.HTTPException(status_code=401, detail="You are not part of an organization")
#     print(user_info.organization.lower())
#     print(user.organization.lower())

#     if user_info.organization.lower() != user_d.organization.lower():
#         raise fastapi.HTTPException(status_code=401, detail="You are not part of {}".format(user_d.organization))

#     return await create_token(user_info)


# @app.post("/logout")
# async def logout_user(user: _schemas.User = fastapi.Depends(is_authenticated)):
#    if await logout(user):
#         return {"message": "logout successful"}


# @app.get("/users/me", response_model=_schemas.User)
# async def get_user(user: _schemas.User = fastapi.Depends(is_authenticated)):
#     return user


# @app.put("/users/me")
# async def update_user(
#     user_update: _schemas.UserUpdate,
#     user: _schemas.User = fastapi.Depends(is_authenticated),
#     db: orm.Session = fastapi.Depends(get_db),
#     ):
#     await user_update(user_update, user, db)

# # ////////////////////////////////////////////////////CODE ////////////////////////////////////////////////////////////// 
# @app.post("/users/resend-verification/code")
# async def resend_code_verification(
#     email : _schemas.UserCodeVerification,
#     db: orm.Session = fastapi.Depends(get_db),
#     ):
#     return await resend_code_verification_mail(email.email, db, email.code_length)

# @app.post("/users/verify/code/{code}")
# async def verify_user_with_code(
#     code: str,
#     db: orm.Session = fastapi.Depends(get_db),
#     ):
#     return await verify_user_code(code)


# @app.post("/users/forgot-password/code")
# async def send_code_password_reset_email(
#     email : _schemas.UserCodeVerification,
#     db: orm.Session = fastapi.Depends(get_db),
#     ):
#     return await send_code_password_reset_email(email.email, db, email.code_length)


# @app.put("/users/password-change/code/{code}")
# async def password_change_with_code(
#     password : _schemas.UserPasswordUpdate,
#     code: str,
#     db: orm.Session = fastapi.Depends(get_db),
#     ):
#     return await password_change_code(password, code, db)

# # ////////////////////////////////////////////////////CODE //////////////////////////////////////////////////////////////



# # ////////////////////////////////////////////////////TOKEN ////////////////////////////////////////////////////////////// 
# @app.post("/users/resend-verification/token")
# async def resend_token_verification(
#     email : _schemas.UserTokenVerification,
#     db: orm.Session = fastapi.Depends(get_db),
#     ):
#     return await resend_token_verification_mail(email.email, email.redirect_url, db)

# @app.post("/users/verify/token/{token}")
# async def verify_user_with_token(
#     token: str,
#     db: orm.Session = fastapi.Depends(get_db),
#     ):
#     return await verify_user_token(token)


# @app.post("/users/forgot-password/token")
# async def send_token_password_reset_email(
#     email : _schemas.UserTokenVerification,
#     db: orm.Session = fastapi.Depends(get_db),
#     ):
#     return await send_token_password_reset_email(email.email, email.redirect_url,db)


# @app.put("/users/password-change/token/{token}")
# async def password_change_with_token(
#     password : _schemas.UserPasswordUpdate,
#     token: str,
#     db: orm.Session = fastapi.Depends(get_db),
#     ):
#     return await password_change_token(password, token, db)

# # ////////////////////////////////////////////////////TOKEN //////////////////////////////////////////////////////////////

# async def get_user_by_email(email: str, db: orm.Session):
#     return db.query(user_models.User).filter(user_models.User.email == email).first()

# async def get_user_by_id(id: str, db: orm.Session):
#     return db.query(user_models.User).filter(user_models.User.id == id).first()


# async def create_user(verification_method: str, user: _schemas.UserCreate, db: orm.Session):
#     verification_info = ""
#     user_obj = user_models.User(
#         id = uuid4().hex,email=user.email, password=_hash.sha256_crypt.hash(user.password),
#         first_name=user.first_name, last_name=user.last_name,
#         is_active=True, is_verified = True
#     )
#     db.add(user_obj)
#     db.commit()

#     # This all needs to be done async in a queue
#     # if verification_method == "code":
#     #     code = await resend_code_verification_mail(user_obj.email, db, user.verification_code_length)
#     #     verification_info = code["code"]
#     # elif verification_method == "token":
#     #     token = await resend_token_verification_mail(user_obj.email,user.verification_redirect_url, db)
#     #     verification_info = token["token"]

#     db.refresh(user_obj)
#     return {"user":user_obj, "verification_info": verification_info}


# async def user_update(user_update: _schemas.UserUpdate, user:_schemas.User, db: orm.Session):
#     user = await get_user_by_id(id = user.id, db=db)

#     if user_update.first_name != "":
#         user.first_name = user_update.first_name

#     if user_update.last_name != "":
#         user.last_name = user_update.last_name

#     if user_update.phone_number != "":
#         user.phone_number = user_update.phone_number
        
#     if user_update.organization != "":
#         user.organization = user_update.organization

#     db.commit()
#     db.refresh(user)

#     return _schemas.User.fromorm(user)


# async def authenticate_user(email: str, password: str, db: orm.Session):
#     user = await get_user_by_email(db=db, email=email)

#     if not user:
#         return False

#     if not user.verify_password(password):
#         return False

#     return user