
from uuid import uuid4
from fastapi import APIRouter, Request, status, responses
from typing import List
import fastapi as fastapi
from fastapi.param_functions import Depends
import fastapi.security as _security
from sqlalchemy import schema
import sqlalchemy.orm as orm
from .schemas import organisation_schemas as _schemas
from bigfastapi.db.database import get_db, db_engine
from .auth import is_authenticated
from .models import organisation_models as _models
import datetime as _dt

from .schemas import settings_schemas 

from .schemas import settings_schemas as schemas 
from .schemas import users_schemas
from .auth import is_authenticated
from .models import settings_models as models
import datetime as _dt



app = APIRouter(tags=["Settings"])


@app.put("/settings", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Settings)

async def update_settings(
    settings: schemas.Settings, 
    db: orm.Session = Depends(get_db),
    # organization: _schemas.Organization = Depends(is_authenticated),
    # user: users_schemas.User = Depends(is_authenticated)
    ):
    # db_settings = get_settings_by_organisation_id(organization_id=organization.id, db=db)
    # if db_settings:
    #     raise fastapi.HTTPException(status_code=400, detail="Settings already exists")
    # return create_settings(settings=settings, db=db, organization=organization)
    # if organization.id == True and user.is_superuser == True:


        settings = models.Settings(
            id=uuid4().hex,
            location=settings.location,
            # organization=settings.organization,
            organization_size=settings.organization_size,
            organization_type=settings.organization_type,
            email=settings.email,
            phone_number=settings.phone_number,
            country=settings.country,
            state=settings.state,
            city=settings.city,
            zip_code=settings.zip_code,)

        db.add(settings)
        db.commit()
        db.refresh(settings)
        return schemas.Settings.from_orm(settings)
    # return responses.JSONResponse({"message": "only an admin can change an organization settings"}, status_code=status.HTTP_401_UNAUTHORIZED)


# @app.get("/settings", status_code=status.HTTP_200_OK, response_model=schemas.Settings)
# async def get_settings(
#     db: orm.Session = Depends(get_db),
#     # organization: _schemas.Organization = Depends(is_authenticated),
#     # user: users_schemas.User = Depends(is_authenticated)
    # ):
    # db_settings = get_settings_by_organisation_id(organization_id=organization.id, db=db)
    # if db_settings:
    #     return schemas.Settings.from_orm(db_settings)
    # return responses.JSONResponse({"message": "Settings not found"}, status_code=status.HTTP_404_NOT_FOUND)
    # if organization.id == True and user.is_superuser == True:
    #     db_settings = get_settings_by_organisation_id(organization_id=organization.id, db=db)
    #     if db_settings:
    #         return schemas.Settings.from_orm(db_settings)
    #     return responses.JSONResponse({"message": "Settings not found"}, status_code=status.HTTP_404_NOT_FOUND)
    # return responses.JSONResponse({"message": "only an admin can change an organization settings"}, status_code=status.HTTP_401_UNAUTHORIZED)



@app.get('/settings/', response_model=List[schemas.SettingsInDB])
def get_settings(db: orm.Session = Depends(get_db)):
    settings = db.query(models.Settings).all()
    return list(map(schemas.SettingsInDB.from_orm, settings))








async def _organization_selector(organization_id: int, user: users_schemas.User, db: _orm.Session):
    organization = (
        db.query(_models.Organization)
        .filter_by(creator=user.id)
        .filter(_models.Organization.id == organization_id)
        .first()
    )

    if organization is None:
        raise _fastapi.HTTPException(status_code=404, detail="Organization does not exist")

    return organization



async def update_organization(organization_id: int, organization: _schemas.OrganizationUpdate, user: users_schemas.User, db: _orm.Session):
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



    

# @app.post("/settings", response_model=settings_schemas.Settings)
# async def create_settings( db: orm.Session = Depends(get_db), settings: settings_schemas.Settings):
#     settings = models.Settings(id=uuid4().hex, location= settings.location, email= settings.email, 
#     phone_number= settings.phone_number, organization_size= settings.organization_size, 
#     organization_type= settings.organization_type, country= settings.country, 
#     state= settings.state, city= settings.city, zip_code= settings.zip_code)   
#     db.add(settings)
#     db.commit()
#     db.refresh(settings)
#     return settings_schemas.Settings.from_orm(settings)
    



# async def create_organization(user: users_schemas.User, db: _orm.Session, organization: _schemas.OrganizationCreate):
#     organization = _models.Organization(id=uuid4().hex, creator=user.id, mission= organization.mission, 
#     vision= organization.vision, values= organization.values, name= organization.name)
#     db.add(organization)
#     db.commit()
#     db.refresh(organization)
#     return _schemas.Organization.from_orm(organization)



