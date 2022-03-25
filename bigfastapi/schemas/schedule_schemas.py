from ast import Str
from datetime import datetime
from sqlite3 import Date
from typing import Dict, List, Optional, Set
from fastapi import Query
from pydantic import BaseModel
from datetime import date as date_type
from enum import Enum


class ScheduleType(str, Enum):
    sms = "SMS"
    email = "EMAIL"
    both = "BOTH"


class ReminderAfterDueDate(str, Enum):
    daily = "DAILY"
    weekly = "WEEKLY"
    MONTHLY = "MONTHLY"


class NumberOfRemindersBeforeDueDate(int, Enum):
    one = 1
    two = 2
    three = 3


class StartReminder(str, Enum):
    Before_due_date = "Before Due Date"
    After_due_date = "After Due Date"


class CreateReminderSchedule(BaseModel):
    organization_id: str
    start_reminder: StartReminder
    no_of_days: int

    class Config:
        orm_mode = True


class UpdateSchedule(BaseModel):
    start_reminder: Optional[StartReminder]
    no_of_days: Optional[int]

    class Config:
        orm_mode = True
