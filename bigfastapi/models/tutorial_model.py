from typing import List
from bigfastapi import db
from uuid import uuid4
from bigfastapi.models import plan_model, user_models
from bigfastapi.schemas import plan_schema, tutorial_schema, users_schemas
from bigfastapi.db.database import get_db
import sqlalchemy.orm as _orm
import fastapi as _fastapi
import bigfastapi.db.database as _database
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime, Boolean, ARRAY, Text
from sqlite3 import IntegrityError
from sqlalchemy import ForeignKey
import datetime as _dt


class Tutorial(_database.Base):
    __tablename__ = "tutorials_main"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    category = Column(String(255), index=True)
    title = Column(String(255), unique=True, index=True)
    description = Column(Text, unique=True, index=True, default="")
    thumbnail = Column(Text, unique=True, index=True, default="")
    stream_url = Column(Text, unique=True, index=True)
    text = Column(Text, index=True, default="")
    added_by = Column(String(255), ForeignKey("users.id"))
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)

#
# SERVICE LAYER


# GENERIC STRUCTURED RESPONSE BUILDER
def buildSuccessRes(resData, isList: bool):
    if isList:
        return tutorial_schema.TutorialListRes(status_code=200, resource_type='plan list', data=resData)
    else:
        return tutorial_schema.TutorialSingleRes(status_code=200, resource_type='plan', data=resData)
