from typing import List
from bigfastapi import db
from uuid import uuid4
from bigfastapi.models import plan_model, user_models
from bigfastapi.schemas import plan_schema, tutorial_schema, users_schemas
from bigfastapi.db.database import get_db
import sqlalchemy.orm as _orm
from fastapi import HTTPException, status
import fastapi as _fastapi
import bigfastapi.db.database as _database
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime, Boolean, ARRAY, Text
from sqlite3 import IntegrityError
from sqlalchemy import ForeignKey
import datetime as _dt
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from operator import or_


class Tutorial(_database.Base):
    __tablename__ = "tutorial"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    category = Column(String(255), index=True)
    title = Column(String(255), index=True)
    description = Column(String(700), index=True, default="")
    thumbnail = Column(String(255), index=True, default="")
    stream_url = Column(String(255), index=True)
    text = Column(String(700), index=True, default="")
    added_by = Column(String(255), ForeignKey("users.id"))
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)


# --------------------------------------------------------------------------------------------------#
#                                    REPOSITORY LAYER
# --------------------------------------------------------------------------------------------------#
#

async def store(newTutorial: tutorial_schema.TutorialRequest, db: _orm.Session):
    objectConstruct = Tutorial(
        id=uuid4().hex, category=newTutorial.category, title=newTutorial.title,
        description=newTutorial.description, thumbnail=newTutorial.thumbnail,
        stream_url=newTutorial.stream_url, text=newTutorial.text, added_by=newTutorial.added_by)
    copy = await findTheSame(db, newTutorial)
    if copy == None:
        try:
            db.add(objectConstruct)
            db.commit()
            db.refresh(objectConstruct)
            return objectConstruct
        except:
            raise HTTPException(
                status_code=500, detail='Server Error')
    else:
        raise HTTPException(
            status_code=500, detail='A tutorial with the same details already exist')


async def getRowCount(db: _orm.Session):
    return db.query(Tutorial).count()


async def getUser(addedBy: str, db: _orm.Session):
    return db.query(user_models.User).filter(user_models.User.id == addedBy).first()


async def findTheSame(db: _orm.Session, request: tutorial_schema.TutorialRequest):
    return db.query(Tutorial).filter(
        request.title == Tutorial.title or request.description == Tutorial.description or
        request.stream_url == Tutorial.stream_url or request.thumbnail == Tutorial.thumbnail or
        request.text == Tutorial.text).first()


async def findReplica(db: _orm.Session, itemId: str, request: tutorial_schema.TutorialRequest):
    return db.query(Tutorial).filter(Tutorial.id != itemId).filter(
        request.title == Tutorial.title or request.description == Tutorial.description or
        request.stream_url == Tutorial.stream_url or request.thumbnail == Tutorial.thumbnail or
        request.text == Tutorial.text).first()


async def groupByCategory(db: _orm.Session, skip: int, limit: int):
    return db.query(
        Tutorial.category, Tutorial.thumbnail,
        func.count(Tutorial.category).label('count')).group_by(
        Tutorial.category).offset(skip).limit(limit).all()


async def fetchAll(db: _orm.Session, skip: int, limit: int):
    return db.query(Tutorial).offset(skip).limit(limit).all()


async def getBytitle(title: str, db: _orm.Session, skip: int, limit: int):
    return db.query(Tutorial).filter(Tutorial.title == title).offset(skip).limit(limit).all()


async def getByCategory(categoryName: str, db: _orm.Session, skip: int, limit: int):
    return db.query(Tutorial).filter(Tutorial.category == categoryName).offset(skip).limit(limit).all()


async def getByCatByTitle(categoryName: str, title: str, db: _orm.Session, skip: int, limit: int):
    return db.query(Tutorial).filter(
        Tutorial.category == categoryName and
        Tutorial.title == title).offset(skip).limit(limit).all()


async def getOne(tutorialId: str, db: _orm.Session):
    return db.query(Tutorial).filter(tutorialId == Tutorial.id).first()


async def searchWithAll(keyword: str, db: _orm.Session, skip: int, limit: int):
    return db.query(Tutorial).filter(or_(
        Tutorial.category.like(keyword),
        Tutorial.title.like(keyword),
        Tutorial.title.like(keyword))).offset(skip).limit(limit).all()


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
                    raise HTTPException(status_code=500, detail='Opp error')
            else:
                raise PermissionError('Lacks super admin access')
        else:
            raise LookupError('Could not find user')
    else:
        raise LookupError('Tutorial does not exisst')


async def update(newTutorial: tutorial_schema.TutorialRequest, itemId: str, userId: str, db: _orm.Session):
    duplicate = await findReplica(db, itemId, newTutorial)
    user = await getUser(userId, db)
    tutorial = await getOne(itemId, db)
    print(duplicate)

    if user:
        if user.is_superuser:
            if duplicate is None:
                try:
                    db.query(Tutorial).filter(tutorial.id == itemId).update(
                        {
                            "category": newTutorial.category,
                            "title": newTutorial.title,
                            "description": newTutorial.description,
                            "text": newTutorial.text,
                            "thumbnail": newTutorial.thumbnail,
                            "stream_url": newTutorial.stream_url,
                            "added_by": newTutorial.added_by,
                            "last_updated": _dt.datetime.utcnow()
                        })
                    db.commit()
                    db.refresh(tutorial)
                    return tutorial
                except:
                    raise HTTPException(
                        status_code=500, detail='Something went wrong')
            else:
                raise HTTPException(
                    status_code=409, detail='Tutorial with the same details already exist')
        else:
            raise PermissionError('Lacks super admin access')
    else:
        raise LookupError('Could not find user')


# GENERIC STRUCTURED RESPONSE BUILDER
def buildSuccessRes(resData, isList: bool):
    if isList:
        return tutorial_schema.TutorialListRes(status_code=200, resource_type='plan list', data=resData)
    else:
        return tutorial_schema.TutorialSingleRes(status_code=200, resource_type='plan', data=resData)
