import datetime
from typing import Text
from uuid import uuid4
import bigfastapi.db.database as db
import sqlalchemy.orm as orm
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Integer

class qrcode(db.Base):
    __tablename__ = "qrcode"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    question = Column(String(255), index=True)
    answer = Column(String(700), index=True)
    created_by = Column(String(255), index=True)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)