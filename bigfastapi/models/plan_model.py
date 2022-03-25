
import datetime as _dt
from operator import index
from sqlite3 import Timestamp
from tkinter.messagebox import CANCEL
from tokenize import Floatnumber
from bigfastapi.models.organisation_models import Organization
from bigfastapi.models.user_models import User
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime, Boolean, ARRAY, Text
from enum import Enum

from uuid import UUID, uuid4


import bigfastapi.db.database as _database


class AccessTypeEnum(str, Enum):
    unlimited = 'unlimited'
    camdown = 'mild'
    limited = 'limited'


class Plan(_database.Base):
    __tablename__ = "plan"

    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    credit_price = Column(Integer, index=True)
    access_type = Column(String(225), index=True,
                         default=AccessTypeEnum.limited)
    duration = Column(Integer, index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)
