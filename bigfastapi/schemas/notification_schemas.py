from datetime import datetime
import pydantic as pydantic
from pydantic import Field
from typing import Optional, List
from fastapi import Depends

class NotificationBase(pydantic.BaseModel):
    content: str
    recipient: str
    reference: str

class Notification(NotificationBase):
    id: str
    creator: str
    has_read: bool
    date_created: datetime
    last_updated: datetime

    class Config:
        orm_mode = True

class NotificationCreate(NotificationBase):
    creator: str = Field(..., description="creator='' makes the authenticated user email the creator. If you want to override it, pass the email you want to use eg. creator='support@admin.com'")

class NotificationUpdate(NotificationBase):
    pass