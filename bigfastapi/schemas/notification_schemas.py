from datetime import datetime
import pydantic as pydantic
from pydantic import Field, EmailStr
from typing import Optional, List
from fastapi import Depends

class NotificationBase(pydantic.BaseModel):
    content: str
    recipient: EmailStr
    reference: str = Field(..., description="model instance reference eg. comment-9cd87677378946d88dc7903b6710ae55", max_length=100)

class Notification(NotificationBase):
    id: str
    creator: EmailStr
    has_read: bool
    date_created: datetime
    last_updated: datetime

    class Config:
        orm_mode = True

class NotificationCreate(NotificationBase):
    creator: EmailStr = Field(..., description="creator='' makes the authenticated user email the creator. If you want to override it, pass the email you want to use eg. creator='support@admin.com'")

class NotificationUpdate(NotificationBase):
    pass