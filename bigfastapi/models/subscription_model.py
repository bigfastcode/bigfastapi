
import datetime as _dt
from operator import index
from sqlite3 import Timestamp
from tkinter.messagebox import CANCEL
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from bigfastapi.models.organisation_models import Organization
from bigfastapi.models.plan_model import Plan
from bigfastapi.models.user_models import User
import passlib.hash as _hash
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime, Boolean, ARRAY, Text
from enum import Enum
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql import func
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE
import bigfastapi.db.database as _database


class SubStatusEnum(str, Enum):
    canceled = "canceled"
    suspended = "suspended"
    active = "active"


class Subscription(_database.Base):
    __tablename__ = "subscription"

    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(225), ForeignKey(Organization.id))
    plan_id = Column(String(225), ForeignKey(Plan.id))
    is_paid = Column(Boolean, default=True, index=True)
    active_status = Column(String(225), index=True,
                           default=SubStatusEnum.active)

    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)
