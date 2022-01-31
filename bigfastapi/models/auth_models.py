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
from ..utils.utils import generate_short_id
from bigfastapi.db import database


class VerificationCode(database.Base):
    __tablename__ = "verification_codes"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    code = Column(String(255), index=True, unique=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)


class PasswordResetCode(database.Base):
    __tablename__ = "password_reset_codes"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    code = Column(String(255), index=True, unique=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)


class Token(database.Base):
    __tablename__ = "tokens"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(String(255), index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)


class VerificationToken(database.Base):
    __tablename__ = "verification_tokens"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    token = Column(String(255), index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)

class PasswordResetToken(database.Base):
    __tablename__ = "password_reset_tokens"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    token = Column(String(255), index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)