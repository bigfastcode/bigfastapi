import datetime as dt
from re import T
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Enum, DateTime, Boolean, ARRAY, Text
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4
from sqlalchemy.sql import func
import bigfastapi.db.database as database


class Schedule(database.Base):
    __tablename__ = "schedules"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), ForeignKey("businesses.id"))
    # when can you start reminding a customer of a debt before due date
    start_reminder = Column(String(255), index=True)
    no_of_days = Column(Integer, index=True)
    is_deleted = Column(Boolean, default=False)
    date_created = Column(DateTime, default=dt.datetime.utcnow)
