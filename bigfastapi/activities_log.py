from decouple import config
from fastapi import APIRouter
import fastapi as _fastapi
from fastapi.param_functions import Depends
from bigfastapi.db.database import get_db
from bigfastapi.models import user_models as userModel
import fastapi as _fastapi
from uuid import uuid4
from bigfastapi.utils import settings as settings
from bigfastapi.schemas.activities_log_schemas import ActivitiesLogBase
from bigfastapi.schemas.activities_log_schemas import ActivitiesLogOutput as ActivitiesSchema
from bigfastapi.schemas.activities_log_schemas import DeleteActivitiesLogBase
from .auth_api import *
from bigfastapi.models.activities_log_models import Activitieslog as ActivitiesModel
from fastapi import APIRouter, Depends, status, HTTPException
from bigfastapi.models.organisation_models import Organization
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import requests



app = APIRouter(tags=["Activitieslog"])

@app.post("/logs/{model_name}/{object_id}")
def addActivitiesLog(
    model_name: str,
    object_id: str,
    log: ActivitiesLogBase,
    background_tasks: BackgroundTasks = BackgroundTasks(), 
    db: Session = Depends(get_db),
    user: str = _fastapi.Depends(is_authenticated),
):

    organization = (db.query(Organization)
        .filter(Organization.id == log.organization_id)
        .filter(Organization.is_deleted == False).first())
        
    if not organization:
        return JSONResponse({"message": "Organization does not exist"},
            status_code=status.HTTP_400_BAD_REQUEST)
    
    #send log to background task
    background_tasks.add_task(createActivityLog, model_name, object_id, user, log,  db)

    return JSONResponse({"message": "log successfully recorded"},
            status_code=status.HTTP_200_OK)


@app.get("/logs/details")
def getActivitiesLog(
    organization_id: str,
    db: Session = Depends(get_db),
    user: str = _fastapi.Depends(is_authenticated),

):
    organization = db.query(Organization).filter(
        Organization.id == organization_id).first()
    if not organization:
        return JSONResponse({"message": "Organization does not exist"},
                            status_code=status.HTTP_400_BAD_REQUEST)

    logs = getOrganizationActivitiesLog(organization_id, db)

    return logs

@app.delete("/logs/{id}")
def deleteActivitiesLog(id: str, body: DeleteActivitiesLogBase, db: Session = Depends(get_db)):
    log = (db.query(ActivitiesModel).filter(ActivitiesModel.id == id)
        .filter(ActivitiesModel.organization_id == body.organization_id)
        .first())

    log.is_deleted = True
    db.commit()
    db.refresh(log)
    return log

@app.delete("/logs")
def deleteAllActivitiesLog(body: DeleteActivitiesLogBase, db: Session = Depends(get_db)):
    logs = (db.query(ActivitiesModel)
            .filter(ActivitiesModel.is_deleted == False)
            .filter(ActivitiesModel.organization_id == body.organization_id))
    
    
    
    for log in logs:
        #log = db.query(ActivitiesModel).filter(ActivitiesModel.id == logger.id).first()
        log.is_deleted = True
        db.commit()
        db.refresh(log)

    return JSONResponse({"message": "deleted successfully"},
            status_code=status.HTTP_200_OK)

#======================= LOG SERVICES ===============================

def createActivityLog(model_name, object_id, user, log, db):
    
    activityLog = ActivitiesModel(
        id= uuid4().hex, organization_id = log.organization_id, 
        user_id= user.id, object_id= object_id, object_url=log.object_url,
        model_name=model_name, action=log.action, created_at=datetime.now()
    )

    db.add(activityLog)
    db.commit()
    db.refresh(activityLog)

    organization = db.query(Organization).filter(
        Organization.id == log.organization_id).first()

    userInfo = db.query(userModel.User).filter(
        userModel.User.id == user.id).first()

    setattr(activityLog, 'user', userInfo)
    setattr(activityLog, 'organization', organization)

    #send request to slack
    requests.post(url=config('LOG_WEBHOOK_URL'), 
        json={"text" : user.first_name +' '+user.last_name +' '+ log.action},headers={"Content-Type": "application/json"}, verify=True
    )

    return activityLog

def getOrganizationActivitiesLog(organization_id, db):
    
    logs = (db.query(ActivitiesModel)
        .filter(ActivitiesModel.organization_id == organization_id)
        .filter(ActivitiesModel.is_deleted == False)
    )
    organization = db.query(Organization).filter(Organization.id == organization_id).first()

    logCollection = list(map(ActivitiesSchema.from_orm, logs))

    for log in logCollection:
        userInfo = (db.query(userModel.User).filter(userModel.User.id == log.user_id).first())
        setattr(log, 'user', userInfo)
        setattr(log, 'organization', organization)
    
    return logCollection
