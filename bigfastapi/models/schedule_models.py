import datetime as dt
from re import T
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Enum, DateTime, Boolean, ARRAY, Text
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4
from sqlalchemy.sql import func
import bigfastapi.db.database as database


class Schedule(database.Base):
    __tablename__ = "scheduless"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(), ForeignKey("businesses.id"))
    # can either be sms, email or both
    schedule_type = Column(String(225), index=True)
    # when can you start reminding a customer of a debt before due date
    start_reminder = Column(String, index=True)
    # intervals or frequency of reminders before due date
    frequency_of_reminder_before_due_date = Column(String, index=True)
    first_template = Column(String, index=True)
    second_template = Column(String, index=True)
    third_template = Column(String, index=True)
    template_after_due_date = Column(String, index=True)
    frequency_of_reminder_after_due_date = Column(String, index=True)
    is_deleted = Column(Boolean, default=False)
    date_created = Column(DateTime, default=dt.datetime.utcnow)
