import datetime as _dt
import os
from uuid import uuid4
from bigfastapi.schemas import roles_schemas

import fastapi as _fastapi
import sqlalchemy.orm as _orm
from decouple import config
from fastapi import APIRouter
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import and_

from bigfastapi.db.database import get_db
from .auth_api import is_authenticated
from .files import upload_image
from .models import credit_wallet_models as credit_wallet_models
from .models import organisation_models as _models
from .models import store_user_model, user_models, store_invite_model, role_models
from .models import wallet_models as wallet_models
from fastapi import BackgroundTasks
from .schemas import organisation_schemas as _schemas
from .schemas import users_schemas

from .utils.utils import paginate_data, row_to_dict

app = APIRouter(tags=["Organization"])


@app.post("/organizations", response_model=_schemas.Organization)
async def create_organization(
        organization: _schemas.OrganizationCreate,
        user: str = _fastapi.Depends(is_authenticated),
        db: _orm.Session = _fastapi.Depends(get_db),
):
    db_org = await get_orgnanization_by_name(name=organization.name, db=db)

    if db_org:
        raise _fastapi.HTTPException(
            status_code=400, detail="Organization name already in use")
    created_org = await create_organization(user=user, db=db, organization=organization)

    if organization.add_template == True:
        template_obj = _models.DefaultTemplates(
            id=uuid4().hex, organization_id=created_org.id, subject="Reminder_One",
            escalation_level=1, email_message="This is the first default email template created for this business.", sms_message="This is the first default sms template created for this business",
            is_deleted=False, greeting="Reminder_Greetings", template_type="BOTH"
        )

        db.add(template_obj)
        db.commit()
        db.refresh(template_obj)

        template_obj = _models.DefaultTemplates(
            id=uuid4().hex, organization_id=created_org.id, subject="Reminder_Two",
            escalation_level=1, email_message="This is the second default email template created for this business.", sms_message="This is the second default sms template created for this business",
            is_deleted=False, greeting="Reminder_Greetings", template_type="BOTH"
        )

        db.add(template_obj)
        db.commit()
        db.refresh(template_obj)

    return created_org


@app.get("/organizations")
async def get_organizations(
        user: users_schemas.User = _fastapi.Depends(is_authenticated),
        db: _orm.Session = _fastapi.Depends(get_db),
        page_size: int = 15,
        page_number: int = 1,
):
    all_orgs = await get_organizations(user, db)

    return paginate_data(all_orgs, page_size, page_number)


@app.get("/organizations/{organization_id}", status_code=200)
async def get_organization(
        organization_id: str,
        user: users_schemas.User = _fastapi.Depends(is_authenticated),
        db: _orm.Session = _fastapi.Depends(get_db),
):
    return await get_organization(organization_id, user, db)


@app.get("/organizations/{organization_id}/users", status_code=200)
async def get_organization_users(
        organization_id: str,
        db: _orm.Session = _fastapi.Depends(get_db)
):

    """
        An endpoint that returns the users in an organization.
    """
    # query the store_users table with the organization_id
    invited_list = db.query(store_user_model.StoreUser).filter(
        and_(
            store_user_model.StoreUser.store_id == organization_id,
            store_user_model.StoreUser.is_deleted == False
        )
    ).all()

    invited_list = list(map(lambda x: row_to_dict(x), invited_list))

    organization = (
        db.query(_models.Organization)
        .filter(_models.Organization.id == organization_id)
        .first()
    )

    if organization is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="Organization does not exist")
    store_owner_id = organization.creator
    store_owner = (
        db.query(user_models.User)
        .filter(user_models.User.id == store_owner_id)
        .first())

    invited_users = []
    if len(invited_list) > 0:
        for invited in invited_list:
            user =  db.query(user_models.User).filter(
                and_(
                    user_models.User.id == invited["user_id"],
                    user_models.User.is_deleted == False
                )).first()
            role = db.query(role_models.Role).filter(
                role_models.Role.id == invited["role_id"]).first()
            if(user.id == invited["user_id"]):
                invited["email"] = user.email
                invited["role"] = role.role_name 

            invited_users.append(invited)

    users = {
        "user":store_owner,
        "invited": invited_users
        }
    return users

@app.delete("/organizations/{organization_id}/users/{user_id}")
def delete_organization_user(
    organization_id: str,
    user_id: str,
    db: _orm.Session = _fastapi.Depends(get_db)
    ):
    # fetch the organization user from the user table
    user = db.query(user_models.User).filter(user_models.User.id == user_id).first()

    if user is not None:
        # fetch the store user from the store user table.
        store_user = (
            db.query(store_user_model.StoreUser)
            .filter(and_(
                store_user_model.StoreUser.user_id == user_id,
                store_user_model.StoreUser.store_id == organization_id
                ))
            .first()
            )
        
        store_user.is_deleted = True
        user.is_deleted = True
        db.add(store_user)
        db.commit()
        db.refresh(store_user)
        db.add(user)
        db.commit()
        db.refresh(user)

        return { "message": f"User with email {user.email} successfully removed from the store" }
    
    return { "message": "User does not exist" }
    

@app.get("/organizations/{organization_id}/roles")
def get_roles(organization_id: str, db: _orm.Session = _fastapi.Depends(get_db)):
    roles = db.query(role_models.Role).filter(role_models.Role.organization_id == organization_id)
    roles = list(map(roles_schemas.Role.from_orm, roles))    

    return roles

@app.post("/organizations/{organization_id}/roles")
def add_role(payload:roles_schemas.AddRole,
            organization_id: str,
            db: _orm.Session = _fastapi.Depends(get_db)
            ):
    
    roles = db.query(role_models.Role).filter(
        role_models.Role.organization_id == organization_id
    ).all()
    if len(roles) < 1:
        existing_role = (
            db.query(role_models.Role)
            .filter(role_models.Role.role_name == payload.role_name.lower())
            .first()
        )
        if existing_role is None:
            role = role_models.Role(
                id=uuid4().hex,
                organization_id=organization_id.strip(),
                role_name=payload.role_name.lower()
            )

            db.add(role)
            db.commit()
            db.refresh(role)
            
            return role
        
        return { "message": "role already exist" }
    return

@app.get("/organizations/invites/{organization_id}")
def get_pending_invites(
    organization_id: str,
    db: _orm.Session = _fastapi.Depends(get_db)
):
    pending_invites = (
        db.query(store_invite_model.StoreInvite)
        .filter(
            and_(store_invite_model.StoreInvite.store_id == organization_id,
                 store_invite_model.StoreInvite.is_deleted == False,
                 store_invite_model.StoreInvite.is_accepted == False,
                 store_invite_model.StoreInvite.is_revoked == False
                 ))
        .all()
    )

    return pending_invites


@app.put("/organizations/{organization_id}", response_model=_schemas.OrganizationUpdate)
async def update_organization(organization_id: str, organization: _schemas.OrganizationUpdate,
                              user: users_schemas.User = _fastapi.Depends(
                                  is_authenticated),
                              db: _orm.Session = _fastapi.Depends(get_db)):
    return await update_organization(organization_id, organization, user, db)


@app.put("/organizations/{organization_id}/update-image")
async def organization_image_upload(organization_id: str, file: UploadFile = File(...),
                                    db: _orm.Session = _fastapi.Depends(
                                        get_db),
                                    user: users_schemas.User = _fastapi.Depends(
                                        is_authenticated)
                                    ):
    org = db.query(_models.Organization).filter(
        _models.Organization.id == organization_id).first()
    # delete existing image
    # if org.image != "":
    #     image = org.image
    #     filename = f"/{org.id}/{image}"

    #     root_location = os.path.abspath("filestorage")
    #     full_image_path =  root_location + filename
    #     os.remove(full_image_path)

    image = await upload_image(file, db, bucket_name=org.id)
    org.image = image
    db.commit()
    db.refresh(org)
    image = org.image

    appBasePath = config('API_URL')
    imageURL = appBasePath + f'/organizations/{organization_id}/image'
    setattr(org, 'image_full_path', imageURL)
    return org


@app.get("/organizations/{organization_id}/image")
async def get_organization_image_upload(organization_id: str, db: _orm.Session = _fastapi.Depends(get_db)):
    org = db.query(_models.Organization).filter(
        _models.Organization.id == organization_id).first()

    image = org.image
    filename = f"/{org.id}/{image}"

    root_location = os.path.abspath("filestorage")
    full_image_path = root_location + filename

    return FileResponse(full_image_path)


@app.delete("/organizations/{organization_id}", status_code=204)
async def delete_organization(organization_id: str, user: users_schemas.User = _fastapi.Depends(is_authenticated),
                              db: _orm.Session = _fastapi.Depends(get_db)):
    return await delete_organization(organization_id, user, db)


# /////////////////////////////////////////////////////////////////////////////////
# Organisation Services

async def get_orgnanization_by_name(name: str, db: _orm.Session):
    return db.query(_models.Organization).filter(_models.Organization.name == name).first()


async def fetch_organization_by_name(name: str, organization_id: str, db: _orm.Session):
    return db.query(_models.Organization).filter(_models.Organization.name == name).filter(
        _models.Organization.id != organization_id).first()


async def create_organization(user: users_schemas.User, db: _orm.Session, organization: _schemas.OrganizationCreate):
    organization_id = uuid4().hex
    organization = _models.Organization(id=organization_id, creator=user.id, mission=organization.mission,
                                        vision=organization.vision, values=organization.values, name=organization.name,
                                        country=organization.country,
                                        state=organization.state, address=organization.address,
                                        tagline=organization.tagline, image=organization.image, is_deleted=False,
                                        current_subscription=organization.current_subscription,
                                        currency_preference=organization.currency_preference)
    
    db.add(organization)
    db.commit()
    db.refresh(organization)
    
    roles = ["Assistant", "Admin", "Owner"]

    for role in roles: 
        new_role = role_models.Role(
            id=uuid4().hex,
            organization_id=organization.id.strip(),
            role_name=role.lower()
        )
        db.add(new_role)
        db.commit()
        db.refresh(new_role)

    await create_wallet(organization_id=organization_id, currency=organization.currency_preference, db=db)
    await create_credit_wallet(organization_id=organization_id, db=db)

    return _schemas.Organization.from_orm(organization)


async def get_organizations(user: users_schemas.User, db: _orm.Session):
    native_orgs = db.query(_models.Organization).filter_by(
        creator=user.id).all()

    invited_orgs_rep = (
        db.query(store_user_model.StoreUser)
        .filter(store_user_model.StoreUser.user_id == user.id)
        .all()
    )

    if len(invited_orgs_rep) < 1:
        # continue to last stage
        organization_list = native_orgs
        organizationCollection = []
        for pos in range(len(organization_list)):
            appBasePath = config('API_URL')
            imageURL = appBasePath + \
                f'/organizations/{organization_list[pos].id}/image'
            setattr(organization_list[pos], 'image_full_path', imageURL)
            organizationCollection.append(organization_list[pos])

        return organizationCollection

    store_id_list = list(map(lambda x: x.store_id, invited_orgs_rep))

    org = []
    for store_id in store_id_list:
        org = org + \
            db.query(_models.Organization).filter(
                _models.Organization.id == store_id).all()

    org_coll = native_orgs + org
    organizationCollection = []
    for pos in range(len(org_coll)):
        appBasePath = config('API_URL')
        imageURL = appBasePath+f'/organizations/{org_coll[pos].id}/image'
        setattr(org_coll[pos], 'image_full_path', imageURL)
        organizationCollection.append(org_coll[pos])

    return organizationCollection


async def _organization_selector(organization_id: str, user: users_schemas.User, db: _orm.Session):
    organization = (
        db.query(_models.Organization)
        .filter(_models.Organization.id == organization_id)
        .first()
    )

    if organization is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="Organization does not exist")

    appBasePath = config('API_URL')
    imageURL = appBasePath + f'/organizations/{organization_id}/image'
    setattr(organization, 'image_full_path', imageURL)

    return organization


async def get_organization(organization_id: str, user: users_schemas.User, db: _orm.Session):
    organization = await _organization_selector(organization_id=organization_id, user=user, db=db)

    return _schemas.Organization.from_orm(organization)


async def delete_organization(organization_id: str, user: users_schemas.User, db: _orm.Session):
    organization = await _organization_selector(organization_id, user, db)

    db.delete(organization)
    db.commit()


async def update_organization(organization_id: str, organization: _schemas.OrganizationUpdate, user: users_schemas.User,
                              db: _orm.Session):
    organization_db = await _organization_selector(organization_id, user, db)
    currencyUpdated = False
    if organization.mission != "":
        organization_db.mission = organization.mission

    if organization.vision != "":
        organization_db.vision = organization.vision

    if organization.values != "":
        organization_db.values = organization.values

    if organization.name != "":
        db_org = await fetch_organization_by_name(name=organization.name, organization_id=organization_id, db=db)

        if db_org:
            raise _fastapi.HTTPException(
                status_code=400, detail="Organization name already in use")
        else:
            organization_db.name = organization.name

    organization_db.email = organization.email

    organization_db.tagline = organization.tagline

    organization_db.phone_number = organization.phone_number

    if organization.country != "":
        organization_db.country = organization.country

    if organization.state != "":
        organization_db.state = organization.state

    if organization.address != "":
        organization_db.address = organization.address

    if organization.currency_preference != "":
        organization_db.currency_preference = organization.currency_preference
        currencyUpdated = True

    organization_db.last_updated = _dt.datetime.utcnow()

    db.commit()
    db.refresh(organization_db)

    # create a new wallet if the currency is changed
    if currencyUpdated:
        await create_wallet(organization_id=organization_id, currency=organization.currency_preference, db=db)

    return _schemas.Organization.from_orm(organization_db)


async def create_wallet(organization_id: str, currency: str, db: _orm.Session):
    currency = currency.upper()
    wallet = db.query(wallet_models.Wallet).filter_by(organization_id=organization_id).filter_by(
        currency_code=currency).first()

    if wallet is None:
        wallet = wallet_models.Wallet(id=uuid4().hex, organization_id=organization_id, balance=0,
                                      currency_code=currency,
                                      last_updated=_dt.datetime.utcnow())

        db.add(wallet)
        db.commit()
        db.refresh(wallet)


async def create_credit_wallet(organization_id: str, db: _orm.Session):
    credit = credit_wallet_models.CreditWallet(id=uuid4().hex, organization_id=organization_id, amount=0,
                                               last_updated=_dt.datetime.utcnow())

    db.add(credit)
    db.commit()
    db.refresh(credit)
