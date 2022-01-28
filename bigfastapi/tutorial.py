from operator import or_
import sqlalchemy
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
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
import datetime as _dt


app = APIRouter(tags=["Tutorials"])


# SAVE TUTORIAL ENDPOINT
@app.post('/tutorial', response_model=tutorial_schema.TutorialSingleRes)
async def store(newTutorial: tutorial_schema.TutorialRequest, db: _orm.Session = _fastapi.Depends(get_db)):
    try:
        tutorial = await saveNewTutorial(newTutorial, db)
        return tutorial_model.buildSuccessRes(tutorial, False)
    except PermissionError as exception:
        raise HTTPException(status_code=401, detail=str(exception))
    except LookupError as exception:
        raise HTTPException(status_code=404, detail=str(exception))


# GET TUTORIALS - Can be filtered by category, title or both
@app.get('/tutorials', response_model=tutorial_schema.TutorialListRes)
async def getTutorials(
        category: str = None, title: str = None,
        page_size: int = 10, page: int = 1,
        db: _orm.Session = _fastapi.Depends(get_db)):

    rowCount = await tutorial_model.getRowCount(db)
    skip = getSkip(page, page_size)

    tutorials = await runFetchQuery(category, title, page_size, skip, rowCount, db)
    return buildSuccessRes(
        tutorials, True, page_size, rowCount,
        getPagination(page, page_size, rowCount, '/tutorials'))


# GET TUTORIALS IN GROUPED OF CATEGORIES
@app.get('/tutorials/group/categories')
async def getGroup(
        page_size: int = 10, page: int = 1,
        db: _orm.Session = _fastapi.Depends(get_db)):

    rowCount = await tutorial_model.getRowCount(db)
    skip = getSkip(page, page_size)
    groupedTutorials = await tutorial_model.groupByCategory(db, skip, page_size)
    pagination = getPagination(
        page, page_size, rowCount, '/tutorials/group/categories')
    return {"data": groupedTutorials, "total": rowCount, "count": page_size, "pagination": pagination}


# GET A LIST OF ALL TUTORIAL CATEGORIES
@app.get('/tutorials/categories')
async def getCategoryLsit(db: _orm.Session = _fastapi.Depends(get_db)):
    tutorials = await tutorial_model.groupByCategory(db)
    categories = buildCategoryList(tutorials)
    return {"data": categories}


async def saveNewTutorial(newTutorial: tutorial_schema.TutorialRequest, db: _orm.Session):
    user = await tutorial_model.getUser(newTutorial.added_by, db)
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


async def delete(itemId: str, userId: str, db: _orm.Session):
    instance = await tutorial_model.getOne(itemId, db)
    userinstnace = await tutorial_model.getUser(userId, db)
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
    user = await tutorial_model.getUser(userId, db)
    tutorial = await tutorial_model.getOne(itemId, db)
    if user:
        if user.is_superuser:
            try:
                tutorial.category = newTutorial.category, tutorial.title = newTutorial.title,
                tutorial.description = newTutorial.description, tutorial.thumbnail = newTutorial.thumbnail,
                tutorial.stream_url = newTutorial.stream_url, tutorial.text = newTutorial.text,
                tutorial.last_updated = _dt.datetime.utcnow
                db.commit()
                db.refresh(tutorial)
                return tutorial
            except:
                raise HTTPException(status_code=500, detail='Server Error')
        else:
            raise PermissionError('Lacks super admin access')
    else:
        raise LookupError('Could not find user')


# HELPER FUNCTIONS

# SKIP and OFFSET
def getSkip(page: int, pageSize: int):
    return (page-1)*pageSize


# PAGINATION LOGIC
def getPagination(page: int, pageSize: int, count: int, endpoint: str):
    paging = {}
    if (pageSize + getSkip(page, pageSize)) >= count:
        paging['next'] = None
        if page > 1:
            paging['previous'] = f"{endpoint}?page={page-1}&page_size={pageSize}"
        else:
            paging['previous'] = None
    else:
        paging['next'] = f"{endpoint}?page={page+1}&page_size={pageSize}"
        if page > 1:
            paging['previous'] = f"{endpoint}?page={page-1}&page_size={pageSize}"
        else:
            paging['previous'] = None

    return paging


# RUN QUERY
async def runFetchQuery(
        category: str, title: str, page_size: int, skip: int,
        rowCount: int, db: _orm.Session = _fastapi.Depends(get_db)):

    if category is None and title is None:
        return await tutorial_model.fetchAll(db, skip, page_size)
    if category is None and title != None:
        return await tutorial_model.getBytitle(title, db, skip, page_size)
    if category != None and title != None:
        return await tutorial_model.getByCatByTitle(category, title, db, skip, page_size)


# BUID CATEGORY LIST
def buildCategoryList(tutorials: List[tutorial_model.Tutorial]):
    categories = []
    for tutorial in tutorials:
        categories.append(tutorial.category)

    return categories


# GENERIC STRUCTURED RESPONSE BUILDER
def buildSuccessRes(resData, isList: bool, pageSize: int, totalCount: int, pagination: dict):
    if isList:
        return tutorial_schema.TutorialListRes(
            data=resData, total=totalCount, count=pageSize, pagination=pagination)
    else:
        return tutorial_schema.TutorialSingleRes(data=resData)
