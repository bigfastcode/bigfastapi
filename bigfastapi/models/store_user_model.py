from dataclasses import Field
import datetime as dt
from email.policy import default
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
from .user_models import User

class StoreUser(database.Base):
    __tablename__ = "store_users"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    store_id = Column(String(255), index=True)
    user_id = Column(String(255), ForeignKey("users.id"))
    role = Column(String(255), index=True)
    is_deleted = Column(Boolean, default=False) 
    date_created = Column(DateTime, default=dt.datetime.utcnow)