from fastapi import APIRouter, Request, BackgroundTasks
from typing import List, Any
import fastapi as _fastapi
from fastapi.param_functions import Depends
import fastapi.security as _security
import sqlalchemy.orm as _orm
from bigfastapi.db.database import get_db

from pyexpat import model
import fastapi as _fastapi
from fastapi import Request
from fastapi.openapi.models import HTTPBearer
import fastapi.security as _security
import jwt as _jwt
import datetime as _dt
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from bigfastapi.models.extra_info_models import ExtraInfo
from bigfastapi.schemas.extra_info_schemas import ExtraInfoBase
from bigfastapi.utils import settings as settings
from bigfastapi.db import database
from bigfastapi.activity_log import createActivityLog
from .auth_api import *

from bigfastapi.schemas import users_schemas
from bigfastapi.services.auth_service import is_authenticated


from fastapi.security import HTTPBearer
# bearerSchema = HTTPBearer()

# JWT_SECRET = settings.JWT_SECRET
# JWT_ALGORITHM = 'HS256'
# JWT_EXP_DELTA_SECONDS = 60 * 5

app = APIRouter(tags=["Extra Info"])


@app.get("/extrainfo/{model_type}", response_model=List[ExtraInfoBase])
def get_all_extra_info_related_to_model(
    model_type: str, db_Session: _orm.Session = Depends(get_db)
):
    """intro-->This endpoint allows you to retrieve all extra info of the same model type. To use this endpoint you need to make a get request to the /extrainfo/{model_type} endpoint 
            paramDesc-->On get request the url takes the parameter, model_type
                param-->model_type: This is the model type of the extra info

    returnDesc--> On sucessful request, it returns 
        returnBody--> an array of extra info
    """
    extrainfos = db_retrieve_all_model_extra_info(
        model_type=model_type, db=db_Session
    )
    return extrainfos


@app.get("/extrainfo/{model_type}/{object_id}", response_model=List[ExtraInfoBase])
def get_all_extrainfo_for_object(
    model_type: str, object_id: str, db_Session=Depends(get_db)
):
    """intro-->This endpoint allows you to retrieve all extrainfo related to a specific object. 
            To use this endpoint you need to make a get request to the /extrainfo/{model_type}/{object_id} endpoint 
            paramDesc-->On get request the url takes two parameters, model_type & object_id
                param-->model_type: This is the model type of the extrainfo
                param-->object_id: This is the id of the object that contains the extrainfo

    returnDesc--> On sucessful request, it returns 
        returnBody--> an array of extra info belonging to an object
    """
    extrainfos = db_retrieve_all_extra_info_for_object(
        object_id=object_id, model_type=model_type, db=db_Session
    )
    return extrainfos


@app.post("/extrainfo/{model_type}/{object_id}", response_model=ExtraInfoBase)
def create_new_extra_info(
    model_type: str,
    object_id: str,
    background_tasks: BackgroundTasks,
    extrainfo: ExtraInfoBase,
    db_Session=Depends(get_db),
    user: users_schemas.User = Depends(is_authenticated)
):
    """intro-->This endpoint is used to create extra info for an object. To use this endpoint you need to make a post request to the /extrainfo/{model_type}/{object_id} endpoint 
            paramDesc-->On post request the url takes two parameters, model_type & object_id
                param-->model_type: This is the model type of the extrainfo
                param-->object_id: This is the id of the object to add

    returnDesc--> On sucessful request, it returns 
        returnBody--> details of the refreshed extra info
    """
    extrainfo = db_create_extra_info_for_object(
        object_id=object_id, extrainfo=extrainfo, model_type=model_type, db=db_Session
    )

    return extrainfo


# SERVICES
def db_retrieve_all_model_extra_info(model_type: str, db: _orm.Session):
    """Retrieve all extra info of model type

    Args:
        model_type (str): Model Type
        db (_orm.Session): [description]

    Returns:
        List[Extrainfo]: QuerySet of all extra info where model_type == model_type
    """
    object_qs = db.query(ExtraInfo).filter(
        ExtraInfo.model_type == model_type).all()

    return object_qs


def db_retrieve_all_extra_info_for_object(object_id: int, model_type: str, db: _orm.Session):
    """Retrieve all extra info related to a specific object

    Args:
        object_id (int): ID of the object that maps to rel_id of the extra info
        model_type (str): Model Type of the object
        db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI

    Returns:
        queryset: A list of all extra info belonging to an object.
    """
    object_qs = db.query(ExtraInfo).filter(ExtraInfo.rel_id == object_id,
                                           ExtraInfo.model_type == model_type).all()

    return object_qs


def db_create_extra_info_for_object(object_id: str, model_type: str, extrainfo: ExtraInfoBase, db: _orm.Session):
    """Create extra info for an object

    Args:
        object_id (str): ID of Object to create extra info for. Maps to rel_id of extra info
        extrainfo (ExtraInfoBase): new extra info data
        db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI
        model_type (str): Model Type of the extra info to create.

    Returns:
        Extrainfo: Data of the newly Created extra info
    """

    id = extrainfo.id if extrainfo.id else uuid4().hex
    obj = ExtraInfo(id=id, rel_id=object_id, model_type=model_type, key=extrainfo.key,
                    value=extrainfo.value, date_created=extrainfo.date_created,
                    last_updated=extrainfo.last_updated)
    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj
