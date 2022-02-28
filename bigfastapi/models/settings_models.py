import datetime as _dt
from re import T
from sqlite3 import Timestamp
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Enum, DateTime, Boolean, ARRAY, Text
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql import func
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE
import bigfastapi.db.database as database


class Settings(database.Base):

    __tablename__ = "settings"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    org_id = Column(String(255), ForeignKey("businesses.id"))
    location = Column(String(255), index=True, nullable=True)
    phone_number = Column(String(255), index=True, nullable=True)
    email = Column(String(255), index=True, nullable=True)
    organization_size = Column(String(255), index=True)
    organization_type = Column(String(255), index=True)
    country = Column(String(255), index=True)
    state = Column(String(255), index=True)
    city = Column(String(255), index=True)
    zip_code = Column(Integer, index=True)










