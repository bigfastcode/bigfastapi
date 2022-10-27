from datetime import datetime
import pydantic as pydantic
from pydantic import Field
from typing import Optional, List
from fastapi import Depends
from enum import Enum

# class NotificationBase(pydantic.BaseModel):
#     content: str
#     recipient: str
#     reference: str

# class Notification(NotificationBase):
#     id: str
#     creator: str
#     has_read: bool
#     date_created: datetime
#     last_updated: datetime

#     class Config:
#         orm_mode = True


class SendVia(str, Enum):
    email = "email"
    in_app = "in_app"
    both = "both"


class NotificationBase(pydantic.BaseModel):
    message: str
    # recipient_ids: List[str]
    organization_id: str
    access_level: str

class Notification(NotificationBase):
    id: str
    creator_id: str
    is_read: bool
    date_created: datetime
    last_updated: datetime

    class Config:
        orm_mode = True

# class NotificationCreate(NotificationBase):
#     creator: str = Field(..., description="creator='' makes the authenticated user email the creator. If you want to override it, pass the email you want to use eg. creator='support@admin.com'")

class NotificationCreate(NotificationBase):
    creator_id: str
    module: str


class NotificationSetting(pydantic.BaseModel): #should a creator_id be present here and in the model?
    organization_id: str
    
    access_level: str
    send_via: SendVia


class NotificationSettingUpdate(NotificationSetting):
    last_updated: datetime = datetime.now()


class NotificationSettingResponse(NotificationSetting):
    id: str
    date_created: datetime
    last_updated: datetime     


class NotificationGroup(pydantic.BaseModel):
    name: str


class NotificationGroupResponse(NotificationGroup):
    id: str
    date_created: datetime
    last_updated: datetime


class NotificationGroupUpdate(NotificationGroup):
    last_updated: datetime = datetime.now()   


class NotificationGroupMember(pydantic.BaseModel):
    group_id: str
    member_id: str     


class NotificationGroupMemberResponse(NotificationGroupMember):
    id: str
    date_created: datetime
    last_updated: datetime  


class NotificationUpdate(NotificationBase):
    pass