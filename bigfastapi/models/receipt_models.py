import datetime as _dt
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
import bigfastapi.db.database as _database

class Receipt(_database.Base):
    __tablename__ = "newreceipts"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    sender_email = Column(String(255), index=True)
    file_id = Column(String(255), ForeignKey("files.id"))
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)
    