from uuid import uuid4

import fastapi as fastapi
import sqlalchemy.orm as orm
from fastapi import APIRouter, status
from fastapi.param_functions import Depends
from sqlalchemy.exc import IntegrityError

from bigfastapi.db.database import get_db
from .auth_api import is_authenticated
from .models import organisation_models as _models
from .models import settings_models as models
from .schemas import settings_schemas as schemas
from .schemas import users_schemas
from typing import List


app = APIRouter(tags=["Settings"])


@app.post("/organization/{org_id}/settings", status_code=status.HTTP_201_CREATED, response_model=schemas.Settings)
async def add_organization_settings(
        org_id: str,
        settings: schemas.Settings,
        db: orm.Session = Depends(get_db),
        user: users_schemas.User = Depends(is_authenticated),
        organization: _models.Organization = Depends(is_authenticated)
):
    try:
        settings = models.Settings(
            id=uuid4().hex,
            location=settings.location,
            org_id=org_id,
            organization_size=settings.organization_size,
            organization_type=settings.organization_type,
            email=settings.email,
            phone_number=settings.phone_number,
            country=settings.country,
            state=settings.state,
            city=settings.city,
            zip_code=settings.zip_code, )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    except:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong, try again",
        )
    return schemas.Settings.from_orm(settings)


### Fetch settings by organization id ####
@app.get('/organization/{org_id}/settings', status_code=status.HTTP_200_OK, response_model=schemas.Settings)
async def get_organization_settings(
        org_id: str,
        db: orm.Session = Depends(get_db),
        user: users_schemas.User = Depends(is_authenticated),
        organization: _models.Organization = Depends(is_authenticated)):
    settings = await fetch_settings(id=org_id, db=db)
    return schemas.Settings.from_orm(settings)


### Update Settings by organization id ####
@app.put('/organization/{org_id}/settings', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.SettingsUpdate)
async def update_organization_settings(
        org_id: str,
        settings: schemas.SettingsUpdate,
        db: orm.Session = Depends(get_db),
        user: users_schemas.User = Depends(is_authenticated),
        organization: _models.Organization = Depends(is_authenticated)):
    return await update_settings(org_id=org_id, settings=settings, db=db)


# APP SETTINGS

@app.get('/settings', response_model=List[schemas.AppSetting])
async def get_app_settings(
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: orm.Session = fastapi.Depends(get_db)
):
    if user.is_superuser:
        results = db.query(models.AppSetting).all()

        return list(results)
    else:
        raise fastapi.HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="You are not allowed to perform this request", )


@app.get('/settings/{name}', response_model=schemas.AppSetting)
async def get_app_setting(
        name: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: orm.Session = fastapi.Depends(get_db)
):
    if user.is_superuser:
        results = db.query(models.AppSetting).filter_by(name=name).first()
        if results is None:
            raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail="Setting does not exist", )
        return results
    else:
        raise fastapi.HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="You are not allowed to perform this request", )


@app.put('/settings/{id}', response_model=schemas.AppSetting)
async def update_app_setting(
        body: schemas.CreateAppSetting,
        id: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: orm.Session = fastapi.Depends(get_db)
):
    if user.is_superuser:
        app_setting = db.query(models.AppSetting).filter_by(id=id).first()
        if app_setting is None:
            raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail="Setting does not exist", )
        app_setting.name = body.name
        app_setting.value = body.value
        db.commit()
        db.refresh(app_setting)

        return app_setting
    else:
        raise fastapi.HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="You are not allowed to perform this request", )


@app.delete('/settings/{id}')
async def delete_app_settings(
        id: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: orm.Session = fastapi.Depends(get_db)
):
    if user.is_superuser:
        # db.query(models.AppSetting).delete()
        # app_settings = []
        try:
            app_setting = db.query(models.AppSetting).filter_by(id=id).first()
            if app_setting is None:
                raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                            detail="Setting does not exist", )

            db.delete(app_setting)
            db.commit()
            return 'deleted'
        except IntegrityError:
            raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="A setting with this name already exists", )

    else:
        raise fastapi.HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="You are not allowed to perform this request", )


@app.post('/settings', response_model=schemas.AppSetting)
async def add_app_settings(
        body: schemas.CreateAppSetting,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: orm.Session = fastapi.Depends(get_db)
):
    if user.is_superuser:
        # db.query(models.AppSetting).delete()
        # app_settings = []
        try:
            app_setting = models.AppSetting(
                id=uuid4().hex,
                name=body.name,
                value=body.value)
            db.add(app_setting)
            db.commit()
            db.refresh(app_setting)
            return app_setting
        except IntegrityError:
            raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="A setting with this name already exists", )

    else:
        raise fastapi.HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="You are not allowed to perform this request", )


####################
#     SERVICES     #
####################

async def fetch_settings(
        id: str,
        db: orm.Session):
    settings = db.query(models.Settings).filter(models.Settings.org_id == id).first()
    if settings == None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settings not found",
        )
    return settings


async def settings_selector(org_id: str, db: orm.Session):
    settings = db.query(models.Settings).filter(models.Settings.org_id == org_id).first()
    if settings == None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settings Does Not Exist",
        )
    return settings


async def update_settings(org_id: str, settings: schemas.SettingsUpdate, db: orm.Session):
    settings_db = await settings_selector(org_id, db)
    if settings.email != "" and settings.email != None:
        settings_db.email = settings.email
    if settings.phone_number != "" and settings.phone_number != None:
        settings_db.phone_number = settings.phone_number
    if settings.country != "" and settings.country != None:
        settings_db.country = settings.country
    if settings.state != "" and settings.state != None:
        settings_db.state = settings.state
    if settings.city != "" and settings.city != None:
        settings_db.city = settings.city
    if settings.zip_code != "" and settings.zip_code != None:
        settings_db.zip_code = settings.zip_code
    if settings.location != "" and settings.location != None:
        settings_db.location = settings.location
    if settings.organization_size != "" and settings.organization_size != None:
        settings_db.organization_size = settings.organization_size
    if settings.organization_type != "" and settings.organization_type != None:
        settings_db.organization_type = settings.organization_type
    db.commit()
    db.refresh(settings_db)
    return schemas.Settings.from_orm(settings_db)
