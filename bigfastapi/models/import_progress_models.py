from cProfile import label
from cgitb import text
import datetime as _dt
from email.policy import default
from locale import currency
from numbers import Number, Real
import select
from sqlite3 import Timestamp
from typing import Optional
from typing import List
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Enum, DateTime, Boolean, ARRAY, Text, Date
from sqlalchemy import JSON, Float, ForeignKey, ARRAY, Float
from uuid import uuid4
#import db.database as _database
import sqlalchemy.orm as orm
import bigfastapi.db.database as _database
import enum

class ImportProgress(_database.Base):
    __tablename__ = "import_progress"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    model = Column(String(255))
    current = Column(String(255))
    end = Column(String(255))
    organization_id = Column(String(255))
    is_deleted= Column(Boolean, default=False)
    updated_at=Column(DateTime, default=_dt.datetime.now())
    created_at=Column(DateTime, default=_dt.datetime.now())