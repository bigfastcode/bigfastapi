from email import message
from sqlalchemy.exc import IntegrityError
from typing import List
from bigfastapi import db, users
from uuid import uuid4
from bigfastapi.models import plan_model, tutorial_model, user_models
from bigfastapi.schemas import plan_schema, tutorial_schema
from bigfastapi.db.database import get_db
import sqlalchemy.orm as _orm
import fastapi as _fastapi
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.param_functions import Depends
from fastapi import APIRouter, HTTPException, status
import fastapi
import sqlalchemy

app = APIRouter(tags=["Tutorials"])


@app.post('/tutorial', response_model=tutorial_schema.TutorialSingleRes)
async def store(newTutorial: tutorial_schema.TutorialRequest, db: _orm.Session = _fastapi.Depends(get_db)):
    try:
        tutorial = await saveNewTutorial(newTutorial, db)
        return tutorial_model.buildSuccessRes(tutorial, False)
    except PermissionError as exception:
        raise HTTPException(status_code=401, detail=str(exception))
    except LookupError as exception:
        raise HTTPException(status_code=404, detail=str(exception))


async def getUser(addedBy: str, db: _orm.Session):
    return db.query(user_models.User).filter(user_models.User.id == addedBy).first()


async def saveNewTutorial(newTutorial: tutorial_schema.TutorialRequest, db: _orm.Session):
    user = await getUser(newTutorial.added_by, db)
    if user != None:
        if user.is_superuser:
            dbRes = await store(newTutorial, db)
            return dbRes
        else:
            raise PermissionError("Lacks super admin access")
    else:
        raise LookupError('Could not find user')


# STORE IN DB
async def store(newTutorial: tutorial_schema.TutorialRequest, db: _orm.Session):
    objectConstruct = tutorial_model.Tutorial(
        id=uuid4().hex, category=newTutorial.category, title=newTutorial.title,
        description=newTutorial.description, thumbnail=newTutorial.thumbnail,
        stream_url=newTutorial.stream_url, added_by=newTutorial.added_by)
    try:
        db.add(objectConstruct)
        db.commit()
        db.refresh(objectConstruct)
        return objectConstruct
    except IntegrityError as e:
        raise HTTPException(
            status_code=409, detail='A tutorial with the same details exist')


# GENERIC STRUCTURED RESPONSE BUILDER
def buildSuccessRes(resData, isList: bool):
    if isList:
        return tutorial_schema.TutorialListRes(status_code='success', resource_type='plan list', data=resData)
    else:
        return tutorial_schema.TutorialSingleRes(status_code='success', resource_type='plan', data=resData)
