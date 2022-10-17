from decouple import config
from fastapi import APIRouter
import fastapi as _fastapi
from fastapi.param_functions import Depends
from bigfastapi.db.database import get_db
from bigfastapi.models import user_models as userModel
import fastapi as _fastapi
from uuid import uuid4
from bigfastapi.utils import settings as settings
from bigfastapi.schemas.activity_log_schemas import ActivitiesLogBase
from bigfastapi.schemas.activity_log_schemas import ActivitiesLogOutput as ActivitiesSchema
from bigfastapi.schemas.activity_log_schemas import DeleteActivitiesLogBase
# from .auth_api import *
from bigfastapi.services.auth_service import is_authenticated
from bigfastapi.models.activity_log_models import Activitylog as ActivitiesModel
from fastapi import APIRouter, Depends, status, HTTPException
from bigfastapi.models.organization_models import Organization
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .core.helpers import Helpers
import requests
from starlette.background import BackgroundTask
from datetime import datetime


app = APIRouter(tags=["Activitieslog"])

@app.post("/logs/{model_name}/{object_id}")
def addActivitiesLog(
    model_name: str,
    object_id: str,
    log: ActivitiesLogBase,
    db: Session = Depends(get_db),
    user: str = _fastapi.Depends(is_authenticated),
):

    """intro-->This endpoint allows you record an activity log. To use this endpoint you need to make a post request to the /logs/{model_name}/{object_id} endpoint

        paramDesc-->On get request, the url takes two parameters
            param-->model_name: This is the model name
            param-->object_id: This is the object id

            reqBody-->action: This is the activity description
            reqBody-->object_url: This is the url link to the log
            reqBody-->organization_id: This is the user's current organization
        
    returnDesc--> On sucessful request, it returns message,
        returnBody--> log successfully recorded
    """

    organization = (db.query(Organization)
        .filter(Organization.id == log.organization_id)
        .filter(Organization.is_deleted == False).first())
        
    if not organization:
        return JSONResponse({"message": "Organization does not exist"},
            status_code=status.HTTP_400_BAD_REQUEST)
    
    #send log to background task
    BackgroundTask(createActivityLog, model_name, object_id, user, log,  db)

    return JSONResponse({"message": "log successfully recorded"},
            status_code=status.HTTP_200_OK)


@app.get("/logs/details")
def getActivitiesLog(
    organization_id: str,    
    db: Session = Depends(get_db),
    user: str = _fastapi.Depends(is_authenticated),

):
    """intro-->This endpoint allows you retrieve details of all logs. To use this endpoint you need to make a get request to the /logs/details endpoint

        paramDesc-->On get request, the url takes the parameter, organization_id
            param-->organization_id: This is the user's current organization
        
    returnDesc--> On sucessful request, it returns 
        returnBody--> details of the organization's activity logs
    """
    organization = db.query(Organization).filter(
        Organization.id == organization_id).first()
    if not organization:
        return JSONResponse({"message": "Organization does not exist"},
                            status_code=status.HTTP_400_BAD_REQUEST)

    logs = getOrganizationActivitiesLog(organization_id, db)

    return logs



@app.delete("/logs/{id}")
def deleteActivitiesLog(id: str, body: DeleteActivitiesLogBase, db: Session = Depends(get_db)):
    """intro-->This endpoint allows you delete a particular log. To use this endpoint you need to make a delete request to the /logs/{id} endpoint

        paramDesc-->On delete request, the url takes the parameter, id
            param-->id: This is the the unique id of the log

            reqBody-->organization_id: This is the user's current organization
        
    returnDesc--> On sucessful request, it returns 
        returnBody--> details of the deleted log
    """
    log = (db.query(ActivitiesModel).filter(ActivitiesModel.id == id)
        .filter(ActivitiesModel.organization_id == body.organization_id)
        .first())

    log.is_deleted = True
    db.commit()
    db.refresh(log)
    return log

@app.delete("/logs")
def deleteAllActivitiesLog(body: DeleteActivitiesLogBase, db: Session = Depends(get_db)):
    """intro-->This endpoint allows you delete all logs in an organization. To use this endpoint you need to make a delete request to the /logs endpoint with a specified body of request

            reqBody-->organization_id: This is the user's current organization
        
    returnDesc--> On sucessful request, it returns message,
        returnBody--> "deleted successfully"
    """
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

def createActivityLog(model_name, model_id, user, log, db, created_for_id: str=None, created_for_model: str=None):
    

    activityLog = ActivitiesModel(
        id= uuid4().hex, 
        organization_id = log["organization_id"], 
        user_id= user.id, 
        # user_name = "",
        model_id= model_id, 
        created_for_id=None if not created_for_id else created_for_id,
        created_for_model=None if not created_for_model else created_for_model,
        object_url=log["object_url"],
        model_name=model_name, action=log["action"], created_at=datetime.now()
    )

    db.add(activityLog)
    db.commit()
    db.refresh(activityLog)

    organization = db.query(Organization).filter(
        Organization.id == activityLog.organization_id).first()

    userInfo = db.query(userModel.User).filter(
        userModel.User.id == user.id).first()

    setattr(activityLog, 'user', userInfo)
    setattr(activityLog, 'organization', organization)

    # send request to slack
    requests.post(url=config('LOG_WEBHOOK_URL'), 
        json={"text" : str(" " if user.first_name is None else user.first_name) +' '+ str(" " if user.last_name is None else user.last_name) +' '+ log["action"]},headers={"Content-Type": "application/json"}, verify=True
    )


    return activityLog


def getOrganizationActivitiesLog(organization_id, db):
    
    logs = (db.query(ActivitiesModel)
        .filter(ActivitiesModel.organization_id == organization_id)
        .filter(ActivitiesModel.is_deleted == False)
    )
    # organization = db.query(Organization).filter(Organization.id == organization_id).first()

    logCollection = list(map(ActivitiesSchema.from_orm, logs))

    # for log in logCollection:
    #     userInfo = (db.query(userModel.User).filter(userModel.User.id == log.user_id).first())
    #     setattr(log, 'user', userInfo)
    #     setattr(log, 'organization', organization)
    
    return logCollection
