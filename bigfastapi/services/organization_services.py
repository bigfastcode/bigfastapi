import datetime as _dt
import os
from uuid import uuid4

import fastapi as _fastapi
from decouple import config
from sqlalchemy import orm
from sqlalchemy import or_, and_
from bigfastapi.core.helpers import Helpers
from bigfastapi.models import contact_info_models
from bigfastapi.models import credit_wallet_models as credit_wallet_models
from bigfastapi.models import location_models
from bigfastapi.models import organization_models as Models
from bigfastapi.models import wallet_models as wallet_models
from bigfastapi.models.extra_info_models import ExtraInfo
from bigfastapi.schemas import organization_schemas as Schemas
from bigfastapi.schemas import users_schemas
from bigfastapi.utils.image_utils import generate_thumbnail_for_image

# placeholder menu. will be removed as soon as the dynamic menu flow is completed
DEFAULT_MENU = {
    "active_menu": ["dashboard", "students", "settings", "more"],
    "hospitality": ["dashboard", "reservations", "customers", "settings", "more"],
    "retail": ["dashboard", "customers", "debts", "payments", "settings", "more"],
    "freelance": ["dashboard", "clients", "invoices", "settings", "more"],
    "more": [
        "reports",
        "invoices",
        "fees",
        "tutorials",
        "logs",
        "marketing",
        "sales",
        "suppliers",
        "debts",
        "receipts",
        "products",
        "payments",
    ],
}

MENU = {
    "active": {
        "menu": ["dashboard", "customers", "debts", "payments", "settings", "more"],
        "more": [
            "reports",
            "invoice",
            "fees",
            "tutorials",
            "sales",
            "debts",
            "receipts",
            "products",
            "payments",
        ],
    },
    "menu_list": {
        "education": {
            "menu": ["dashboard", "student", "settings", "more"],
            "more": [
                "reports",
                "invoice",
                "fees",
                "tutorials",
                "sales",
                "debts",
                "receipts",
                "products",
                "payments",
            ],
        },
        "hospitality": {
            "menu": ["dashboard", "reservations", "customers", "settings", "more"],
            "more": [
                "reports",
                "invoice",
                "fees",
                "tutorials",
                "sales",
                "debts",
                "receipts",
                "products",
                "payments",
            ],
        },
        "retail": {
            "menu": ["dashboard", "customers", "debts", "payments", "settings", "more"],
            "more": [
                "reports",
                "invoice",
                "fees",
                "tutorials",
                "sales",
                "debts",
                "receipts",
                "products",
                "payments",
            ],
        },
        "freelance": {
            "menu": ["dashboard", "clients", "settings", "more"],
            "more": [
                "reports",
                "invoice",
                "fees",
                "tutorials",
                "sales",
                "debts",
                "receipts",
                "products",
                "payments",
            ],
        },
    },
}


def create_organization(
    user: users_schemas.User,
    db: orm.Session,
    organization: Schemas.OrganizationCreate,
    contact_infos=[],
    location=[],
):
    organization_id = uuid4().hex
    new_organization = Models.Organization(
        id=organization_id,
        user_id=user.id,
        mission=organization.mission,
        vision=organization.vision,
        name=organization.name,
        business_type=organization.business_type,
        tagline=organization.tagline,
        image_url=organization.image_url,
        is_deleted=False,
        currency_code=organization.currency_code,
    )

    db.add(new_organization)
    db.commit()
    db.refresh(new_organization)

    if organization.location != None:
        for location in organization.location:
            location_id = uuid4().hex
            organization_location = Models.OrganizationLocation(
                id=location_id,
                country=location.country,
                state=location.state,
                county=location.county,
                zip_code=location.zip_code,
                full_address=location.full_address,
                street=location.street,
                significant_landmark=location.significant_landmark,
                driving_instructions=location.driving_instructions,
                longitude=location.longitude,
                latitude=location.latitude,
                association_id=uuid4().hex,
                location_id=location_id,
                organization_id=organization_id,
            )
            db.add(organization_location)
            db.commit()
            db.refresh(organization_location)

    if organization.contact_infos != None:
        for contact_info in organization.contact_infos:
            contact_info_id = uuid4().hex
            organization_contact = Models.OrganizationContactInfo(
                id=contact_info_id,
                contact_data=contact_info.contact_data,
                contact_tag=contact_info.contact_tag,
                contact_type=contact_info.contact_type,
                contact_title=contact_info.contact_title,
                phone_country_code=contact_info.phone_country_code,
                description=contact_info.description,
                association_id=uuid4().hex,
                contact_info_id=contact_info_id,
                organization_id=organization_id,
            )

            db.add(organization_contact)
            db.commit()
            db.refresh(organization_contact)

    return new_organization


def get_organization_by_name(name: str, creator_id: str, db: orm.Session):
    return (
        db.query(Models.Organization)
        .filter(
            Models.Organization.name == name, Models.Organization.user_id == creator_id
        )
        .first()
    )


async def fetch_organization_by_name(name: str, organization_id: str, db: orm.Session):
    return (
        db.query(Models.Organization)
        .filter(Models.Organization.name == name)
        .filter(Models.Organization.id != organization_id)
        .first()
    )


def run_wallet_creation(newOrganization: Models.Organization, db: orm.Session):
    roles = ["Assistant", "Admin", "Owner"]
    for role in roles:
        new_role = Models.Role(
            id=uuid4().hex,
            organization_id=newOrganization.id.strip(),
            role_name=role.lower(),
        )
        db.add(new_role)
        db.commit()
        db.refresh(new_role)

    create_wallet(
        organization_id=newOrganization.id,
        currency=newOrganization.currency_code,
        db=db,
    )
    create_credit_wallet(organization_id=newOrganization.id, db=db)


def create_org_image_full_path(organization, db: orm.Session, width=60, height=60):
    root_location = os.path.abspath(os.environ.get("FILES_BASE_FOLDER", "filestorage"))
    image_folder = os.environ.get("IMAGES_FOLDER", "images")
    image_url = organization.image_url.strip("/")

    # if image url is set and exists, set image_full_path to thumbnail path
    if (image_url != "" and os.path.exists(os.path.join(root_location, image_url))):
        appBasePath = config("API_URL")
        filename = image_url.split("/")[-1]
        size = (width, height)
        key = f"{filename}_{organization.id}_{size}"
        thumbnail = db.query(ExtraInfo).filter(ExtraInfo.key==key).first()

        # if thumbnail in db and thumbnail path not exists, create thumbnail and set image_full_path
        if thumbnail and not os.path.exists(os.path.join(root_location, image_folder, thumbnail.value)):
            thumbnail = generate_thumbnail_for_image(
                full_image_path=os.path.join(root_location, image_url),
                unique_id=organization.id,
                width=size[0], height=size[1]
            )
            imageURL = appBasePath + f"/{thumbnail.value}"
            setattr(organization, "image_full_path", imageURL)
        
        # if thumbnail in db and thumbnail path exists set image_full_path
        elif thumbnail and os.path.exists(os.path.join(root_location, image_folder, thumbnail.value)):
            imageURL = appBasePath + f"/{thumbnail.value}"
            setattr(organization, "image_full_path", imageURL)
        
        # if thumbnail not in db but image path exists
        else:
            thumbnail = generate_thumbnail_for_image(
                full_image_path=os.path.join(root_location, image_url),
                unique_id=organization.id,
                width=size[0], height=size[1]
            )
            imageURL = appBasePath + f"/{thumbnail.value}"
            setattr(organization, "image_full_path", imageURL)


def get_organizations(user: users_schemas.User, db: orm.Session, timestamp: str = None):
    # filter by start and end date if provided

    if timestamp is not None:
        native_orgs = (
            db.query(Models.Organization)
            .filter(Models.Organization.user_id == user.id)
            .filter(or_(Models.Organization.date_created > timestamp, Models.Organization.last_updated_db > timestamp))
            .all()
        )
    else:
        native_orgs = (
            db.query(Models.Organization)
            .filter(Models.Organization.user_id == user.id)
            .all()
        )
    # native_orgs = db.query(Models.Organization).filter_by(user_id=user.id).all()

    invited_orgs_pvt = (
        db.query(Models.OrganizationUser)
        .filter(Models.OrganizationUser.user_id == user.id)

        .all()
    )

    if len(invited_orgs_pvt) == 0:
        organization_list = native_orgs
        organization_collection = []
        for pos in range(len(organization_list)):
            organization = organization_list[pos]
            create_org_image_full_path(organization, db)
            organization_collection.append(organization)

        return organization_collection

    # organization_id_list = list(
    #     map(lambda x: x.organization_id, invited_orgs_pvt))

    # invited
    organization_id_list = []

    for org in invited_orgs_pvt:
        organization_id_list.append(org.organization_id)

    # invited
    invited_orgs = []
    for org_id in organization_id_list:
        invited_orgs.append(
            db.query(Models.Organization)
            .filter(Models.Organization.id == org_id)
            .first()
        )

    org_coll = native_orgs + invited_orgs
    organizationCollection = []

    for pos in range(len(org_coll)):
        organization = org_coll[pos]
        create_org_image_full_path(organization, db)
        organizationCollection.append(organization)

    return organizationCollection



async def organization_selector(
    organization_id: str, user: users_schemas.User, db: orm.Session
):
    organization = (
        db.query(Models.Organization)
        .filter(Models.Organization.id == organization_id)
        .first()
    )

    if organization is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="Organization does not exist"
        )

    create_org_image_full_path(organization, db)

    return organization


async def get_organization(
    organization_id: str, user: users_schemas.User, db: orm.Session
):
    organization = await organization_selector(
        organization_id=organization_id, user=user, db=db
    )

    return organization


async def delete_organization(
    organization_id: str, user: users_schemas.User, db: orm.Session
):
    organization = await organization_selector(organization_id, user, db)

    db.delete(organization)
    db.commit()


async def update_organization(
    organization_id: str,
    organization: Schemas.OrganizationUpdate,
    user: users_schemas.User,
    db: orm.Session,
):
    organization_db = await organization_selector(organization_id, user, db)
    currencyUpdated = False

    organization_dict = organization.dict()
    for key, value in organization_dict.items():
        if value:
            if key in ["name", "contact_infos", "location"]:
                continue
            if key == "currency_code":
                currencyUpdated = True

            setattr(organization_db, key, value)

    if organization.name != None:
        db_org = await fetch_organization_by_name(
            name=organization.name, organization_id=organization_id, db=db
        )

        if db_org and db_org.id != organization_id:
            raise _fastapi.HTTPException(
                status_code=400, detail="Organization name already in use"
            )
        else:
            organization_db.name = organization.name

    # contact infos
    if organization.contact_infos:
        for contact_info in organization.contact_infos:
            contact_info_db = (
                db.query(Models.OrganizationContactInfo)
                .filter(
                    and_(
                        Models.OrganizationContactInfo.organization_id == organization_id,
                        Models.OrganizationContactInfo.contact_type == contact_info.contact_type
                    )
                )
                .first()
            )

            if contact_info_db:
                contact_info_dict = contact_info.dict()
                for key, value in contact_info_dict.items():
                    if value:
                        setattr(contact_info_db, key, value)
            else:
                contact_info_id = uuid4().hex
                organization_contact = Models.OrganizationContactInfo(
                    id=contact_info_id,
                    contact_data=contact_info.contact_data,
                    contact_tag=contact_info.contact_tag,
                    contact_type=contact_info.contact_type,
                    contact_title=contact_info.contact_title,
                    phone_country_code=contact_info.phone_country_code,
                    description=contact_info.description,
                    association_id=uuid4().hex,
                    contact_info_id=contact_info_id,
                    organization_id=organization_id,
                )
                db.add(organization_contact)
        db.commit()

    # location
    if organization.location:
        for location in organization.location:
            location_db = (
                db.query(Models.OrganizationLocation)
                .filter(
                    Models.OrganizationLocation.organization_id == organization_id
                )
                .first()
            )

            if location_db:
                location_dict = location.dict()
                for key, value in location_dict.items():
                    if value:
                        setattr(location_db, key, value)
            else:
                location_id = uuid4().hex
                organization_location = Models.OrganizationLocation(
                    id=location_id,
                    country=location.country,
                    state=location.state,
                    county=location.county,
                    zip_code=location.zip_code,
                    full_address=location.full_address,
                    street=location.street,
                    significant_landmark=location.significant_landmark,
                    driving_instructions=location.driving_instructions,
                    longitude=location.longitude,
                    latitude=location.latitude,
                    association_id=uuid4().hex,
                    location_id=location_id,
                    organization_id=organization_id,
                )
                db.add(organization_location)
        db.commit()

    organization_db.last_updated = _dt.datetime.utcnow()

    db.commit()
    db.refresh(organization_db)

    # create a new wallet if the currency is changed
    if currencyUpdated == True:
        create_wallet(
            organization_id=organization_id, currency=organization.currency_code, db=db
        )

    # menu = get_organization_menu(organization_id, db)

    return {"data": {"organization": organization_db, "menu": DEFAULT_MENU}}


def create_wallet(organization_id: str, currency: str, db: orm.Session):
    currency = currency.upper()
    wallet = (
        db.query(wallet_models.Wallet)
        .filter_by(organization_id=organization_id)
        .filter_by(currency_code=currency)
        .first()
    )

    if wallet is None:
        wallet = wallet_models.Wallet(
            id=uuid4().hex,
            organization_id=organization_id,
            balance=0,
            currency_code=currency,
            last_updated=_dt.datetime.utcnow(),
        )

        db.add(wallet)
        db.commit()
        db.refresh(wallet)


def create_credit_wallet(organization_id: str, db: orm.Session):
    default_credit_wallet_balance = int(config("DEFAULT_CREDIT_WALLET_BALANCE"))
    credit = credit_wallet_models.CreditWallet(
        id=uuid4().hex,
        organization_id=organization_id,
        amount=default_credit_wallet_balance,
        last_updated=_dt.datetime.utcnow(),
    )

    db.add(credit)
    db.commit()
    db.refresh(credit)


def send_slack_notification(user, organization):
    message = user + " created a new organization : " + organization.name
    # sends the message to slack
    Helpers.slack_notification("LOG_WEBHOOK_URL", text=message)


def drop_role_by_name(role_name, db):
    roles = db.query(Models.Role).filter(
        Models.Role.role_name==role_name
    ).all()

    if not roles:
        raise _fastapi.HTTPException(
            status_code=404, detail=f"No role with name {role_name} found"
        )
    
    for role in roles:
        db.query(Models.OrganizationUser).filter(
            Models.OrganizationUser.role_id==role.id
        ).update({"role_id": None})

        db.query(Models.OrganizationInvite).filter(
            Models.OrganizationInvite.role_id==role.id
        ).update({"role_id": None})

        db.delete(role)
        db.commit()

    return True


async def fetch_role(
    organization_id,
    role_name,
    db,
):
    """Get roles for an Organization"""

    role = (
        db.query(Models.Role)
        .filter(and_(
            Models.Role.organization_id == organization_id,
            Models.Role.role_name == role_name
        ))
        .first()
    )

    return role

async def create_role(
    organization_id,
    role_name,
    db,
):
    """Create Role for an Organization"""

    role = Models.Role(
        id=uuid4().hex,
        organization_id=organization_id,
        role_name=role_name,
    )

    db.add(role)
    db.commit()
    db.refresh(role)

    return role


def send_slack_notification_for_org_invite(
    user,
    organization_id,
    recipient,
    db: orm.Session,
    action: str = "sent an invite"
):
    organization = (
            db.query(Models.Organization)
            .filter(Models.Organization.id == organization_id)
            .first()
        )
    if organization is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="Organization does not exist"
        )
    organization_name = organization.name
    
    if user != None:
        if user.first_name is None and user.last_name is None:
            sender = user.email
        else:
            sender = f"{user.first_name if user.first_name else ''} {user.last_name if user.last_name else ''}"

    if action == "accepted invite":
        message = f"{recipient} {action} to join {organization_name}"

    elif action == "declined invite":
        message = f"{recipient} {action} to join {organization_name}"

    elif action == "revoked invite":
        message = f"{sender} {action} earlier sent to {recipient} to join {organization_name}"
        
    else:                    
        message = f"{sender} {action} to {recipient} to join {organization_name}"
    print(message)

    Helpers.slack_notification("LOG_WEBHOOK_URL", text=message)

