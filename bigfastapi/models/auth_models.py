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
from .utils import generate_short_id
import bigfastapi.db.database as _database


class VerificationCode(_database.Base):
    __tablename__ = "verification_codes"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    code = Column(String(255), index=True, unique=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)


class PasswordResetCode(_database.Base):
    __tablename__ = "password_reset_codes"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    code = Column(String(255), index=True, unique=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)


class Token(_database.Base):
    __tablename__ = "tokens"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    token = Column(String(255), index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)

class VerificationToken(_database.Base):
    __tablename__ = "verification_tokens"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    token = Column(String(255), index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)

class PasswordResetToken(_database.Base):
    __tablename__ = "password_reset_tokens"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    token = Column(String(255), index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)