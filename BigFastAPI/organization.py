
from fastapi import APIRouter, Request
from typing import List
import fastapi as _fastapi
from fastapi.param_functions import Depends
import fastapi.security as _security
import sqlalchemy.orm as _orm
from . import services as _services, schema as _schemas
from BigFastAPI.database import get_db

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



