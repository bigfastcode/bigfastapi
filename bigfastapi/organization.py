import datetime as _dt
import os
from uuid import uuid4

import fastapi as _fastapi
import sqlalchemy.orm as _orm
from decouple import config
from fastapi import APIRouter
from fastapi import UploadFile, File
from fastapi.responses import FileResponse

from bigfastapi.db.database import get_db
from .auth_api import is_authenticated
from .files import upload_image
from .models import organisation_models as _models
from .models import wallet_models as wallet_models
from .schemas import organisation_schemas as _schemas
from .schemas import users_schemas
from .utils.utils import paginate_data

app = APIRouter(tags=["Organization"])


@app.post("/organizations", response_model=_schemas.Organization)
async def create_organization(
        organization: _schemas.OrganizationCreate,
        user: str = _fastapi.Depends(is_authenticated),
        db: _orm.Session = _fastapi.Depends(get_db),
):
    db_org = await get_orgnanization_by_name(name=organization.name, db=db)
    if db_org:
        raise _fastapi.HTTPException(status_code=400, detail="Organization name already in use")
    return await create_organization(user=user, db=db, organization=organization)


@app.get("/organizations")
async def get_organizations(
        user: users_schemas.User = _fastapi.Depends(is_authenticated),
        db: _orm.Session = _fastapi.Depends(get_db),
        page_size: int = 15,
        page_number: int = 1,
):
    allorgs = await get_organizations(user, db)
    return paginate_data(allorgs, page_size, page_number)


@app.get("/organizations/{organization_id}", status_code=200)
async def get_organization(
        organization_id: str,
        user: users_schemas.User = _fastapi.Depends(is_authenticated),
        db: _orm.Session = _fastapi.Depends(get_db),
):
    return await get_organization(organization_id, user, db)


@app.get("/organizations/users/{organization_id}", status_code=200)
async def get_organization_users(
        organization_id: str,
        db: _orm.Session = _fastapi.Depends(get_db)
):
    pass


@app.put("/organizations/{organization_id}", response_model=_schemas.OrganizationUpdate)
async def update_organization(organization_id: str, organization: _schemas.OrganizationUpdate,
                              user: users_schemas.User = _fastapi.Depends(is_authenticated),
                              db: _orm.Session = _fastapi.Depends(get_db)):
    return await update_organization(organization_id, organization, user, db)


@app.put("/organizations/{organization_id}/update-image")
async def organization_image_upload(organization_id: str, file: UploadFile = File(...),
                                    db: _orm.Session = _fastapi.Depends(get_db),
                                    user: users_schemas.User = _fastapi.Depends(is_authenticated)
                                    ):
    org = db.query(_models.Organization).filter(_models.Organization.id == organization_id).first()
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
    org = db.query(_models.Organization).filter(_models.Organization.id == organization_id).first()

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

    await create_wallet(organization_id=organization_id, currency=organization.currency_preference, db=db)
    return _schemas.Organization.from_orm(organization)


async def get_organizations(user: users_schemas.User, db: _orm.Session):
    organizations = db.query(_models.Organization).filter_by(creator=user.id)

    organizationlist = list(map(_schemas.Organization.from_orm, organizations))
    organizationCollection = []
    for pos in range(len(organizationlist)):
        appBasePath = config('API_URL')

        imageURL = appBasePath + f'/organizations/{organizationlist[pos].id}/image'
        setattr(organizationlist[pos], 'image_full_path', imageURL)
        organizationCollection.append(organizationlist[pos])

    return organizationCollection


async def _organization_selector(organization_id: str, user: users_schemas.User, db: _orm.Session):
    organization = (
        db.query(_models.Organization)
            .filter_by(creator=user.id)
            .filter(_models.Organization.id == organization_id)
            .first()
    )

    if organization is None:
        raise _fastapi.HTTPException(status_code=404, detail="Organization does not exist")

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
            raise _fastapi.HTTPException(status_code=400, detail="Organization name already in use")
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
