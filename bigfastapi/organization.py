
from fastapi import APIRouter, Request
from typing import List
import fastapi as _fastapi
from fastapi.param_functions import Depends
import fastapi.security as _security
import sqlalchemy.orm as _orm
from . import services as _services, schema as _schemas
from bigfastapi.db.database import get_db

app = APIRouter(tags=["Organization"])

@app.post("/organizations", response_model=_schemas.Organization)
async def create_organization(
    organization: _schemas.OrganizationCreate,
    user: _schemas.User = _fastapi.Depends(_services.is_authenticated),
    db: _orm.Session = _fastapi.Depends(get_db),
):
    db_org = await _services.get_orgnanization_by_name(name = organization.name, db=db)
    print(db_org)
    if db_org:
        raise _fastapi.HTTPException(status_code=400, detail="Organization name already in use")
    return await _services.create_organization(user=user, db=db, organization=organization)


@app.get("/organizations", response_model=List[_schemas.Organization])
async def get_organizations(
    user: _schemas.User = _fastapi.Depends(_services.is_authenticated),
    db: _orm.Session = _fastapi.Depends(get_db),
):
    return await _services.get_organizations(user=user, db=db)


@app.get("/organizations/{organization_id}", status_code=200)
async def get_organization(
    organization_id: int,
    user: _schemas.User = _fastapi.Depends(_services.is_authenticated),
    db: _orm.Session = _fastapi.Depends(get_db),
):
    return await _services.get_organization(organization_id, user, db)



# /////////////////////////////////////////////////////////////////////////////////
# Organisation Services

async def get_orgnanization_by_name(name: str, db: _orm.Session):
    return db.query(_models.Organization).filter(_models.Organization.name == name).first()



async def create_organization(user: _schemas.User, db: _orm.Session, organization: _schemas.OrganizationCreate):
    organization = _models.Organization(id=uuid4().hex, creator=user.id, mission= organization.mission, 
    vision= organization.vision, values= organization.values, name= organization.name)
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return _schemas.Organization.from_orm(organization)


async def get_organizations(user: _schemas.User, db: _orm.Session):
    organizations = db.query(_models.Organization).filter_by(owner_id=user.id)

    return list(map(_schemas.Organization.from_orm, organizations))


async def _organization_selector(organization_id: int, user: _schemas.User, db: _orm.Session):
    organization = (
        db.query(_models.Organization)
        .filter_by(creator=user.id)
        .filter(_models.Organization.id == organization_id)
        .first()
    )

    if organization is None:
        raise _fastapi.HTTPException(status_code=404, detail="Organization does not exist")

    return organization


async def get_organization(organization_id: int, user: _schemas.User, db: _orm.Session):
    organization = await _organization_selector(organization_id=organization_id, user=user, db=db)

    return _schemas.Organization.from_orm(organization)


async def delete_organization(organization_id: int, user: _schemas.User, db: _orm.Session):
    organization = await _organization_selector(organization_id, user, db)

    db.delete(organization)
    db.commit()

async def update_organization(organization_id: int, organization: _schemas.OrganizationUpdate, user: _schemas.User, db: _orm.Session):
    organization_db = await _organization_selector(organization_id, user, db)

    if organization.mission != "":
        organization_db.mission = organization.mission

    if organization.vision != "":
        organization_db.vision = organization.vision

    if organization.values != "":
        organization_db.values = organization.values

    if organization.name != "":
        db_org = await get_orgnanization_by_name(name = organization.name, db=db)
        if db_org:
            raise _fastapi.HTTPException(status_code=400, detail="Organization name already in use")
        else:
            organization_db.name = organization.name       

    organization_db.last_updated = _dt.datetime.utcnow()

    db.commit()
    db.refresh(organization_db)

    return _schemas.Organization.from_orm(organization_db)