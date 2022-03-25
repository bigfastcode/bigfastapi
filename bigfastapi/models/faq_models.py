import datetime as dt
from sqlite3 import Timestamp
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Boolean, Text
from sqlalchemy import ForeignKey
from uuid import uuid4

from sqlalchemy.sql import func
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE
import bigfastapi.db.database as database
from bigfastapi.utils import utils


class Ticket(database.Base):
    __tablename__ = "ticket"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    short_id = Column(String(255), index=True, unique=True,
                      default=utils.generate_short_id())
    title = Column(String(255), index=True)
    issue = Column(String(700), index=True)
    opened_by = Column(String(255), index=True)
    closed = Column(Boolean, default=False, index=True)
    closed_by = Column(String(255), default=None, nullable=True, index=True)
    date_created = Column(DateTime, default=dt.datetime.utcnow)


class Faq(database.Base):
    __tablename__ = "faq"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    question = Column(String(255), index=True)
    answer = Column(String(700), index=True)
    created_by = Column(String(255), index=True)
    date_created = Column(DateTime, default=dt.datetime.utcnow)


class TicketReply(database.Base):
    __tablename__ = "ticketreply"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    ticket_id = Column(String(255), ForeignKey("ticket.id"))
    reply = Column(String(700), index=True)
    reply_by = Column(String(255), default=None, nullable=True, index=True)
    date_created = Column(DateTime, default=dt.datetime.utcnow)
