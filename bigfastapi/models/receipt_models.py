import datetime as _dt
from email.policy import default
from gzip import READ
from re import T
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Text
from sqlalchemy import ForeignKey, and_
from uuid import uuid4
import bigfastapi.db.database as _database
import sqlalchemy.orm as orm
from fastapi import Depends
from bigfastapi.db.database import get_db
from ..models.organisation_models import Organization
from ..schemas import receipt_schemas



class Receipt(_database.Base):
    __tablename__ = "newreceipts"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), index=True)
    sender_email = Column(String(255), index=True)
    message = Column(Text(length=600), index=True)
    subject = Column(String(255), index=True)
    recipient = Column(String(255), index=True)
    file_id = Column(String(255), ForeignKey("files.id"), default=None)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)
