from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Text
from uuid import uuid4
from bigfastapi.db import database
import datetime as dt


class Contact(database.Base):
    __tablename__ = "contact"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    address = Column(String(500), index=True)
    phone = Column(String(255), index=True)
    map_coordinates = Column(String(255), index=True)
    date_created = Column(DateTime, default=dt.datetime.utcnow)
    last_updated = Column(DateTime, default=dt.datetime.utcnow)


class ContactUS(database.Base):
    __tablename__ = "contact us"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    name = Column(String(255), index=True)
    email = Column(String(255), index=True)
    subject = Column(String(255), index=True)
    message = Column(String(255), index=True)
    date_created = Column(DateTime, default=dt.datetime.utcnow)