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

class StoreInvite(database.Base):
    __tablename__ = "store_invites"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    store_id = Column(String(255), ForeignKey("businesses.id"))
    user_id = Column(String(255), ForeignKey("users.id"))
    user_email = Column(String(255), index=True)
    role_id = Column(String(255), ForeignKey("roles.id"))
    invite_code = Column(String(255), index=True)
    is_accepted = Column(Boolean, default=False)
    is_revoked = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False) 
    date_created = Column(DateTime, default=dt.datetime.utcnow)
    
    class Config:
        orm_mode = True