from operator import or_
import sqlalchemy
import fastapi
from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Depends
from fastapi.responses import JSONResponse
from fastapi import APIRouter
import fastapi as _fastapi
import sqlalchemy.orm as _orm
from bigfastapi.db.database import get_db
from bigfastapi.schemas import plan_schema, tutorial_schema
from bigfastapi.models import plan_model, tutorial_model, user_models
from uuid import uuid4
from bigfastapi import db, users
from typing import List
from ast import With
from email import message
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func


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


@app.get('/tutorials/list/categories')
async def getCategoryLsit(db: _orm.Session = _fastapi.Depends(get_db)):
    categories = await groupByCategory(db)


@app.get('/tutorials')
async def getTutorials(category: str = None, db: _orm.Session = _fastapi.Depends(get_db)):
    tutorials = await tutorial_model.groupByCategory(db)
    return tutorials


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
        stream_url=newTutorial.stream_url, text=newTutorial.text, added_by=newTutorial.added_by)
    try:
        db.add(objectConstruct)
        db.commit()
        db.refresh(objectConstruct)
        return objectConstruct
    except IntegrityError as e:
        raise HTTPException(
            status_code=409, detail='A tutorial with the same details exist')


async def getUser(addedBy: str, db: _orm.Session):
    return db.query(user_models.User).filter(user_models.User.id == addedBy).first()


async def groupByCategory(db: _orm.Session):
    return db.query(
        tutorial_model.Tutorial.category, tutorial_model.Tutorial.stream_url,
        func.count(tutorial_model.Tutorial.category).label('count')).group_by(
        tutorial_model.Tutorial.category).all()


async def fetchAll(db: _orm.Session):
    return db.query(tutorial_model.Tutorial).all()


async def getOne(tutorialId: str, db: _orm.Session):
    return db.query(tutorial_model.Tutorial).filter(tutorialId == tutorial_model.Tutorial.id).first()


async def getByCategory(categoryName: str, db: _orm.Session):
    return db.query(tutorial_model.Tutorial).filter(tutorial_model.Tutorial.category == categoryName).all()


async def getBytitle(title: str, db: _orm.Session):
    return db.query(tutorial_model.Tutorial).filter(tutorial_model.Tutorial.title == title).all()


async def searchWithAll(categoryName: str, title: str, desc: str, db: _orm.Session):
    return db.query(tutorial_model.Tutorial).filter(or_(
        tutorial_model.Tutorial.category.like(categoryName),
        tutorial_model.Tutorial.title.like(title),
        tutorial_model.Tutorial.title.like(desc))).all()


async def delete(itemId: str, userId: str, db: _orm.Session):
    instance = await getOne(itemId, db)
    userinstnace = await getUser(userId, db)
    if instance:
        if userinstnace:
            if userinstnace.is_superuser:
                try:
                    db.delete(instance)
                    db.commit()
                    return {"message": "Tutorial deleted succesfully"}
                except:
                    raise HTTPException(status_code=500, detail='Server Error')
            else:
                raise PermissionError('Lacks super admin access')
        else:
            raise LookupError('Could not find user')
    else:
        raise LookupError('Tutorial does not exisst')


async def update(newTutorial: tutorial_schema.TutorialRequest, itemId: str, userId: str, db: _orm.Session):
    user = await getUser(userId, db)
    tutorial = await getOne(itemId, db)
    if user:
        if user.is_superuser:
            db.query(tutorial_model.Tutorial).filter(itemId == tutorial_model.Tutorial.id).update(

            )
            objectConstruct = tutorial_model.Tutorial(
                category=newTutorial.category, title=newTutorial.title,
                description=newTutorial.description, thumbnail=newTutorial.thumbnail,
                stream_url=newTutorial.stream_url, text=newTutorial.text, added_by=newTutorial.added_by)
        else:
            raise PermissionError('Lacks super admin access')
    else:
        raise LookupError('Could not find user')


# GENERIC STRUCTURED RESPONSE BUILDER


def buildSuccessRes(resData, isList: bool):
    if isList:
        return tutorial_schema.TutorialListRes(status_code='success', resource_type='tutoria list', data=resData)
    else:
        return tutorial_schema.TutorialSingleRes(status_code='success', resource_type='tutorial', data=resData)
