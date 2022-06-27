import datetime as dt
import enum
from email.policy import default
import bigfastapi.db.database as database
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime
from sqlalchemy.ext.mutable import MutableList
from uuid import uuid4
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Enum, DateTime, Boolean, ARRAY, Text, JSON
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4
from sqlalchemy.sql import func

class EmailStatus(enum.Enum):
    scheduled = "SCHEDULED"
    sent = "SENT"
    failed = "FAILED"

class Email(database.Base):
    __tablename__ = "email"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), ForeignKey("organizations.id"), nullable=True, index=True)
    title = Column(String(225))
    recipients = Column(JSON, default=[])
    body = Column(String(255), nullable=False)
    is_scheduled = Column(Boolean, default=False, index=True)
    scheduled_time = Column(DateTime)
    status = Column(Enum(EmailStatus), index=True)
    is_deleted = Column(Boolean, default=False)
    email_purpose = Column(String(225), index=True)
    date_created = Column(DateTime, default=dt.datetime.utcnow)






