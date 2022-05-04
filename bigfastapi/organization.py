import datetime as _dt
import os
from uuid import uuid4

import fastapi as _fastapi
import sqlalchemy.orm as _orm
from decouple import config

from fastapi import APIRouter, Depends, BackgroundTasks, FastAPI
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import and_

from bigfastapi.db.database import get_db
from bigfastapi.models import organisation_models
from bigfastapi.models.menu_model import addDefaultMenuList, getOrgMenu
from bigfastapi.schemas import roles_schemas
from .auth_api import is_authenticated
from .files import upload_image
from .models import credit_wallet_models as credit_wallet_models
from .models import organisation_models as _models
from .models import store_user_model, user_models, store_invite_model, role_models, schedule_models
from .models import wallet_models as wallet_models
from .schemas import organisation_schemas as _schemas
from .schemas import users_schemas
from .utils.utils import paginate_data, row_to_dict

app = APIRouter(tags=["Organization"])


@app.post("/organizations")
def create_organization(
        organization: _schemas.OrganizationCreate,
        background_tasks: BackgroundTasks,
        user: str = _fastapi.Depends(is_authenticated),
        db: _orm.Session = _fastapi.Depends(get_db),
):
    """intro-->This endpoint allows you to create a new organization. To use this endpoint you need to make a post request to the /organization endpoint with a specified body of request

            reqBody-->mission: This is the mission f the organization
            reqBody-->vision: This is the vision of the organization
            reqBody-->name: This is the name of the organization
            reqBody-->country: This is the organization's country of operation
            reqBody-->state: This is the organization's state of operation
            reqBody-->address: This is a descriptive address of where the organization is located
            reqBody-->currency_preference: This is the currency of preference of the organization
            reqBody-->phone_number: This is the phone contact detail of the organization
            reqBody-->email This is the email contact address of the organization
            reqBody-->current_subscription: This is the current subscription plan of the organization
            reqBody-->tagline: This is a tagline to identify the organization with
            reqBody-->image: This is a link to cover image for the organization
            reqBody-->values: This describes the values of the organization
            reqBody-->business_type: This is the type of business the organization runs
            reqBody-->credit_balance: This is a value representing the organization's credit balance
            reqBody-->image_full_path: This is full url path to the company's cover image
            reqBody-->add_template: This is a boolean value that determines wether to add already available templates for the organization.
        
    returnDesc--> On sucessful request, it returns
        returnBody--> details of the newly created organization
    """
    db_org = get_orgnanization_by_name(name=organization.name, db=db)

    if db_org:
        raise _fastapi.HTTPException(
            status_code=400, detail="Organization name already in use")
    created_org = create_organization(
        user=user, db=db, organization=organization)

    assocMenu = addDefaultMenuList(
        created_org.id, created_org.business_type, db)

    runWalletCreation(created_org, db)

    background_tasks.add_task(defaults_for_org, organization, created_org, db)

    newOrId = created_org.id
    newOrg = created_org
    newMenList = assocMenu["menu_list"]
    newMenu = assocMenu

    return {"data": {"business": newOrg, "menu": newMenu}}


async def defaults_for_org(organization, created_org, db: _orm.Session):
    defaultTemplates = [
        {
            "escalation_level": 1,
            "email_message":
                'Trust this meets you well This is to remind you that your payment for $debt is due. Please take a moment to make the payment by clicking here - $paymentlink. If you have any questions dont hesitate to reply to this email.',
            "subject": 'Reminder: Your Debt Is Due',
            "sms_message":
                'a kind reminder that your debt of $amount is due. Please click the this link to pay the balance owed - ',
        },
        {

            "escalation_level": 2,
            "email_message":
                'Trust this meets you well Your debt with us is overdue and you have limited time to clear it. Please click here to pay - $paymentLink or request for payment options.',
            "subject": 'Important',
            "sms_message":
                'your debt of $amount is overdue. To clear it, click this link to pay - '
        },
        {

            "escalation_level": 3,

            "email_message":
                'We are yet to receive your overdue payment for $debt. This is becoming really problematic for us and a late payment fee will be applied. Please settle your outstanding balance immediately to avoid this. Click here to pay - $paymentLink',
            "subject":
                'Payment Reminder: Pay Debt Today to Avoid Late Payment Chargest',
            "sms_message":
                'your long overdue debt of $amount has not been paid, please make payment to avoid charges. Pay here - ',
        },
        {

            "escalation_level": 4,
            "subject": 'Alert',
            "email_message":
                'This is a reminder that your debt is now overdue by weeks since the due date and a late payment fee now applies. Please arrange your payment today.',
            "sms_message":
                ' your debt of $amount has not been paid despite previous reminders and a late payment fee now applies. Hurry and pay now - ',

        },
    ]

    defaultSchedules = [
        {
            "no_of_days": 2,
            "repeat_every": 'DAY',
            "start_reminder": 'Before Due Date',
        },
        {
            "no_of_days": 5,
            "repeat_every": 'WEEK',
            "start_reminder": 'After Due Date',
        },
    ]

    if organization.add_template == True:
        try:

            for temp in defaultTemplates:
                template_obj = organisation_models.DefaultTemplates(
                    id=uuid4(
                    ).hex, organization_id=created_org.id, subject=temp["subject"],
                    escalation_level=temp["escalation_level"], email_message=temp["email_message"],
                    sms_message=temp["sms_message"],
                    is_deleted=False, template_type="BOTH"
                )

                db.add(template_obj)
                db.commit()
                db.refresh(template_obj)

        except:
            print("ail To Create Templates")

        try:
            for schedule in defaultSchedules:
                schedule_obj = schedule_models.Schedule(
                    id=uuid4().hex, organization_id=created_org.id,
                    start_reminder=schedule["start_reminder"],
                    repeat_every=schedule["repeat_every"],
                    no_of_days=schedule["no_of_days"],
                    is_deleted=False,
                )

                db.add(schedule_obj)
                db.commit()
                db.refresh(schedule_obj)

        except:
            print("didn't work")

        try:

            autoreminder_obj = organisation_models.DefaultAutoReminder(
                id=uuid4().hex, organization_id=created_org.id, days_before_debt=3,
                first_template="escalation_level_1", second_template="escalation_level_3")

            db.add(autoreminder_obj)
            db.commit()
            db.refresh(autoreminder_obj)

        except:
            print('could not create auto reminder default')


# @app.post("/st-paul")
# def st_paul(db: _orm.Session = _fastapi.Depends(get_db)):
#     orgs = db.query(_models.Organization).filter(
#         _models.Organization.is_deleted == False).all()

#     print(len(orgs))

#     for org in orgs:
#         dt_org = db.query(schedule_models.Schedule).filter(
#             schedule_models.Schedule.organization_id == org.id).all()

#         if len(dt_org) == 0:

#             defaultSchedules = [
#                 {
#                     "no_of_days": 2,
#                     "repeat_every": 'DAY',
#                     "start_reminder": 'Before Due Date',
#                 },
#                 {
#                     "no_of_days": 5,
#                     "repeat_every": 'WEEK',
#                     "start_reminder": 'After Due Date',
#                 },
#             ]

#             for schedule in defaultSchedules:
#                 schedule_obj = schedule_models.Schedule(
#                     id=uuid4().hex, organization_id=org.id,
#                     start_reminder=schedule["start_reminder"],
#                     repeat_every=schedule["repeat_every"],
#                     no_of_days=schedule["no_of_days"],
#                     is_deleted=False,
#                 )

#                 db.add(schedule_obj)
#                 db.commit()
#                 db.refresh(schedule_obj)


@app.get("/organizations")
def get_organizations(
        user: users_schemas.User = _fastapi.Depends(is_authenticated),
        db: _orm.Session = _fastapi.Depends(get_db),
        page_size: int = 15,
        page_number: int = 1,
):  
    """intro-->This endpoint allows you to retrieve all organizations. To use this endpoint you need to make a get request to the /organizations endpoint 

            paramDesc-->On get request, the request url takes two(2) optional query parameters
                param-->page_size: This is the size per page, this is 10 by default
                param-->page_number: This is the page of interest, this is 1 by default
        
    returnDesc--> On sucessful request, it returns 
        returnBody--> a list of organizations
    """ 
    all_orgs = get_organizations(user, db)

    return paginate_data(all_orgs, page_size, page_number)


@app.get("/organizations/{organization_id}", status_code=200)
async def get_organization(
        organization_id: str,
        user: users_schemas.User = _fastapi.Depends(is_authenticated),
        db: _orm.Session = _fastapi.Depends(get_db),
):  
    """intro-->This endpoint allows you to retrieve details of a particular organizations. To use this endpoint you need to make a get request to the /organizations/{organization_id} endpoint 

            paramDesc-->On get request, the request url takes the parameter, organization id
                param-->organization_id: This is unique Id of the organization of interest
        
    returnDesc--> On sucessful request, it returns 
        returnBody--> details of the queried organization
    """ 
    organization = await get_organization(organization_id, user, db)
    menu = getOrgMenu(organization_id, db)
    return {"data": {"organization": organization, "menu": menu}}


@app.get("/organizations/{organization_id}/users", status_code=200)
async def get_organization_users(
        organization_id: str,
        db: _orm.Session = _fastapi.Depends(get_db)
):
    """intro-->This endpoint allows you to get all users in an organization. To use this endpoint you need to make a get request to the /organizations/{organization_id}/users endpoint 

        paramDesc-->On get request, the request url takes the parameter, organization id
            param-->organization_id: This is unique Id of the organization of interest
        
    returnDesc--> On sucessful request, it returns the 
        returnBody--> details of all users in the queried organization
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
            user = db.query(user_models.User).filter(
                and_(
                    user_models.User.id == invited["user_id"],
                    user_models.User.is_deleted == False
                )).first()
            role = db.query(role_models.Role).filter(
                role_models.Role.id == invited["role_id"]).first()
            if (user.id == invited["user_id"]):
                invited["email"] = user.email
                invited["role"] = role.role_name

            invited_users.append(invited)

    users = {
        "user": store_owner,
        "invited": invited_users
    }
    return users


@app.delete("/organizations/{organization_id}/users/{user_id}")
def delete_organization_user(
        organization_id: str,
        user_id: str,
        db: _orm.Session = _fastapi.Depends(get_db)
):  
    """intro-->This endpoint allows you to delete a particular user from an organization. To use this endpoint you need to make a delete request to the /organizations/{organization_id}/users/{user_id} endpoint 

        paramDesc-->On delete request, the request url takes two(2) parameters, organization id and user id
            param-->organization_id: This is unique Id of the organization of interest
            param-->user_id: This is the unique id of the user to be removed from the organization
        
    returnDesc--> On sucessful request, it returns message,
        returnBody--> User with email {email} successfully removed from the store
    """
    # fetch the organization user from the user table
    user = db.query(user_models.User).filter(
        user_models.User.id == user_id).first()

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

        return {"message": f"User with email {user.email} successfully removed from the store"}

    return {"message": "User does not exist"}


@app.get("/organizations/{organization_id}/roles")
def get_roles(organization_id: str, db: _orm.Session = _fastapi.Depends(get_db)):
    """intro-->This endpoint allows you to retrieve all available roles in an organization. To use this endpoint you need to make a get request to the /organizations/{organization_id}/roles endpoint 

        paramDesc-->On get request, the request url takes the parameter, organization id 
            param-->organization_id: This is the unique Id of the organization of interest
        
    returnDesc--> On sucessful request, it returns,
        returnBody--> all available roles in the queried organization
    """
    roles = db.query(role_models.Role).filter(
        role_models.Role.organization_id == organization_id)
    roles = list(map(roles_schemas.Role.from_orm, roles))

    return roles


@app.post("/organizations/{organization_id}/roles")
def add_role(payload: roles_schemas.AddRole,
             organization_id: str,
             db: _orm.Session = _fastapi.Depends(get_db)
             ):
    """intro-->This endpoint allows you to create roles in an organization. To use this endpoint you need to make a post request to the /organizations/{organization_id}/roles endpoint with a specified body of request

        paramDesc-->On get request, the request url takes the parameter, organization id 
            param-->organization_id: This is the unique Id of the organization of interest

            reqBody-->organization_id: This is a unique Id of the organization of interest
            reqBody-->role_name: This is the name of the new role to be created in the organization
        
    returnDesc--> On sucessful request, it returns,
        returnBody--> details of the newly created organization role
    """
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

        return {"message": "role already exist"}
    return


@app.get("/organizations/invites/{organization_id}")
def get_pending_invites(
        organization_id: str,
        db: _orm.Session = _fastapi.Depends(get_db)
):  
    """intro-->This endpoint allows you to retrieve all pending invites to an organization. To use this endpoint you need to make a get request to the /organizations/invites/{organization_id} endpoint

        paramDesc-->On get request, the request url takes the parameter, organization id 
            param-->organization_id: This is the unique Id of the organization of interest

        
    returnDesc--> On sucessful request, it returns,
        returnBody--> all pending invites in the queried organization
    """
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


@app.put("/organizations/{organization_id}")
async def update_organization(organization_id: str, organization: _schemas.OrganizationUpdate,
                              user: users_schemas.User = _fastapi.Depends(
                                  is_authenticated),
                              db: _orm.Session = _fastapi.Depends(get_db)):
    """intro-->This endpoint allows you to update the details of a particular organization organization. To use this endpoint you need to make a put request to the /organizations/{organization_id} endpoint with a specified body of request

        paramDesc-->On put request, the request url takes the parameter, organization id 
            param-->organization_id: This is the unique Id of the organization of interest

            reqBody-->mission: This is the mission f the organization
            reqBody-->vision: This is the vision of the organization
            reqBody-->name: This is the name of the organization
            reqBody-->country: This is the organization's country of operation
            reqBody-->state: This is the organization's state of operation
            reqBody-->address: This is a descriptive address of where the organization is located
            reqBody-->currency_preference: This is the currency of preference of the organization
            reqBody-->phone_number: This is the phone contact detail of the organization
            reqBody-->email This is the email contact address of the organization
            reqBody-->current_subscription: This is the current subscription plan of the organization
            reqBody-->tagline: This is a tagline to identify the organization with
            reqBody-->image: This is a link to cover image for the organization
            reqBody-->values: This describes the values of the organization
            reqBody-->business_type: This is the type of business the organization runs
            reqBody-->credit_balance: This is a value representing the organization's credit balance
            reqBody-->image_full_path: This is full url path to the company's cover image
            reqBody-->add_template: This is a boolean value that determines wether to add already available templates for the organization.
        
    returnDesc--> On sucessful request, it returns,
        returnBody--> details of the updated organization
    """
    return await update_organization(organization_id, organization, user, db)


@app.put("/organizations/{organization_id}/update-image")
async def organization_image_upload(organization_id: str, file: UploadFile = File(...),
                                    db: _orm.Session = _fastapi.Depends(
                                        get_db),
                                    user: users_schemas.User = _fastapi.Depends(
                                        is_authenticated)
                                    ):
    """intro-->This endpoint allows you to update the cover image of an organization. To use this endpoint you need to make a put request to the /organizations/{organization_id}/update-image endpoint with a specified body of request

        paramDesc-->On put request, the request url takes the parameter, organization id 
            param-->organization_id: This is the unique Id of the organization of interest
        
    returnDesc--> On sucessful request, it returns,
        returnBody--> details of the updated organization
    """
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
    """intro-->This endpoint allows you to retrieve the cover image of an organization. To use this endpoint you need to make a get request to the /organizations/{organization_id}/image endpoint

        paramDesc-->On get request, the request url takes the parameter, organization id 
            param-->organization_id: This is the unique Id of the organization of interest
        
    returnDesc--> On sucessful request, it returns the
        returnBody--> full_image_path property of the organization
    """
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
    """intro-->This endpoint allows you to delete an organization. To use this endpoint you need to make a delete request to the /organizations/{organization_id} endpoint

        paramDesc-->On delete request, the request url takes the parameter, organization id 
            param-->organization_id: This is the unique Id of the organization of interest
        
    returnDesc--> On sucessful request, it returns
        returnBody--> "success"
    """
    return await delete_organization(organization_id, user, db)


# /////////////////////////////////////////////////////////////////////////////////
# Organisation Services

def get_orgnanization_by_name(name: str, db: _orm.Session):
    return db.query(_models.Organization).filter(_models.Organization.name == name).first()


async def fetch_organization_by_name(name: str, organization_id: str, db: _orm.Session):
    return db.query(_models.Organization).filter(_models.Organization.name == name).filter(
        _models.Organization.id != organization_id).first()


def create_organization(user: users_schemas.User, db: _orm.Session, organization: _schemas.OrganizationCreate):
    organization_id = uuid4().hex
    newOrganization = _models.Organization(id=organization_id, creator=user.id, mission=organization.mission,
                                           vision=organization.vision, values=organization.values,
                                           name=organization.name,
                                           country=organization.country, business_type=organization.business_type,
                                           state=organization.state, address=organization.address,
                                           tagline=organization.tagline, image=organization.image, is_deleted=False,
                                           current_subscription=organization.current_subscription,
                                           currency_preference=organization.currency_preference)

    db.add(newOrganization)
    db.commit()
    db.refresh(newOrganization)
    return newOrganization


def runWalletCreation(newOrganization: organisation_models.Organization, db: _orm.Session):
    roles = ["Assistant", "Admin", "Owner"]
    for role in roles:
        new_role = role_models.Role(
            id=uuid4().hex,
            organization_id=newOrganization.id.strip(),
            role_name=role.lower()
        )
        db.add(new_role)
        db.commit()
        db.refresh(new_role)

    create_wallet(organization_id=newOrganization.id,
                  currency=newOrganization.currency_preference, db=db)
    create_credit_wallet(organization_id=newOrganization.id, db=db)


def get_organizations(user: users_schemas.User, db: _orm.Session):
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
        imageURL = appBasePath + f'/organizations/{org_coll[pos].id}/image'
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
    organization = await _organization_selector(
        organization_id=organization_id, user=user, db=db)

    return organization


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
        create_wallet(organization_id=organization_id,
                      currency=organization.currency_preference, db=db)

    menu = getOrgMenu(organization_id, db)

    return {"data": {"organization": organization_db, "menu": menu}}


def create_wallet(organization_id: str, currency: str, db: _orm.Session):
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


def create_credit_wallet(organization_id: str, db: _orm.Session):
    default_credit_wallet_balance = int(
        config('DEFAULT_CREDIT_WALLET_BALANCE'))
    credit = credit_wallet_models.CreditWallet(id=uuid4().hex, organization_id=organization_id,
                                               amount=default_credit_wallet_balance,
                                               last_updated=_dt.datetime.utcnow())

    db.add(credit)
    db.commit()
    db.refresh(credit)
