
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
from utils import utils

class Ticket(_database.Base):
    __tablename__ = "ticket"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    short_id = Column(String(255), index=True, unique=True, default=utils.generate_short_id())
    title = Column(String(255), index=True)
    issue = Column(Text(), index=True)
    opened_by = Column(String(255), index=True)
    closed = Column(Boolean, default=False, index=True)
    closed_by = Column(String(255), default=None, nullable=True, index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)

class Faq(_database.Base):
    __tablename__ = "faq"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    question = Column(String(255), index=True)
    answer = Column(Text(), index=True)
    created_by = Column(String(255), index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)

class TicketReply(_database.Base):
    __tablename__ = "ticketreply"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    ticket_id = Column(String(255), ForeignKey("ticket.id"))
    reply = Column(Text(), index=True) 
    reply_by = Column(String(255), default=None, nullable=True, index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)

