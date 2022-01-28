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
    __tablename__ = "instructions"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    category = Column(String(255), index=True)
    title = Column(String(255), unique=True, index=True)
    description = Column(Text, unique=True, index=True, default="")
    thumbnail = Column(Text, index=True, default="")
    stream_url = Column(Text, index=True)
    text = Column(Text, index=True, default="")
    added_by = Column(String(255), ForeignKey("users.id"))
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)


#
# SERVICE LAYER
async def store(newTutorial: tutorial_schema.TutorialRequest, db: _orm.Session):
    objectConstruct = Tutorial(
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


async def getRowCount(db: _orm.Session):
    return db.query(Tutorial).count()


async def getUser(addedBy: str, db: _orm.Session):
    return db.query(user_models.User).filter(user_models.User.id == addedBy).first()


async def groupByCategory(db: _orm.Session):
    return db.query(
        Tutorial.category, Tutorial.stream_url,
        func.count(Tutorial.category).label('count')).group_by(
        Tutorial.category).all()


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


async def searchWithAll(
        categoryName: str, title: str, desc: str, db: _orm.Session, skip: int, limit: int):
    return db.query(Tutorial).filter(or_(
        Tutorial.category.like(categoryName),
        Tutorial.title.like(title),
        Tutorial.title.like(desc))).offset(skip).limit(limit).all()


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


# GENERIC STRUCTURED RESPONSE BUILDER


def buildSuccessRes(resData, isList: bool):
    if isList:
        return tutorial_schema.TutorialListRes(status_code=200, resource_type='plan list', data=resData)
    else:
        return tutorial_schema.TutorialSingleRes(status_code=200, resource_type='plan', data=resData)
