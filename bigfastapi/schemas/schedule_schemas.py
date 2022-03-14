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
    One_Week = "ONE_WEEK before due date"
    Two_Weeks = "TWO_WEEKS before due date"
    Three_Weeks = "THREE_WEEKS before due date"
    Four_Weeks = "FOUR_WEEKS before due date"


class ReminderBeforeDueDate(str, Enum):
    once_a_week = "ONCE_A_WEEK"
    twice_a_week = "TWICE_A_WEEK"
    once_a_month = "ONCE_A_MONTH"


class CreateReminderSchedule(BaseModel):
    organization_id: str
    schedule_type: ScheduleType
    # when to start reminder before due date
    start_reminder: StartReminder
    frequency_of_reminder_before_due_date: ReminderBeforeDueDate
    first_template: Optional[str]
    second_template: Optional[str]
    third_template: Optional[str]
    template_after_due_date: str
    frequency_of_reminder_after_due_date: ReminderAfterDueDate

    class Config:
        orm_mode = True


class UpdateSchedule(BaseModel):
    organization_id: str
    schedule_type: Optional[ScheduleType]
    # when to start reminder before due date
    start_reminder: Optional[StartReminder]
    frequency_of_reminder_before_due_date: Optional[ReminderBeforeDueDate]
    first_template: Optional[str]
    second_template: Optional[str]
    third_template: Optional[str]
    template_after_due_date: Optional[str]
    frequency_of_reminder_after_due_date: Optional[ReminderAfterDueDate]

    class Config:
        orm_mode = True
