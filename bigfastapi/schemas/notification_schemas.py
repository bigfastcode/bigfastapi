from datetime import datetime
import pydantic as pydantic
from pydantic import Field
from typing import Any, Optional, List
from fastapi import Depends
from enum import Enum


class SendVia(str, Enum):
    email = "email"
    in_app = "in_app"
    both = "both"


class NotificationCreator(pydantic.BaseModel):
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]

    class Config:
        orm_mode = True


class NotificationStatus(pydantic.BaseModel):
    is_read: Optional[bool]
    is_cleared: Optional[bool]


class NotificationBase(pydantic.BaseModel):
    message: str
    organization_id: str
    access_level: str


class Notification(NotificationBase):
    id: str
    creator_id: str
    date_created: datetime
    last_updated: datetime
    creator: Optional[NotificationCreator]

    class Config:
        orm_mode = True


class NotificationRecipientResponse(NotificationBase):
    id: str
    creator_id: str
    is_read: Optional[bool] = False
    is_cleared: Optional[bool] = False
    date_created: datetime
    last_updated: datetime

    class Config:
        orm_mode = True

# class NotificationCreate(NotificationBase):
#     creator: str = Field(..., description="creator='' makes the authenticated user email the creator. If you want to override it, pass the email you want to use eg. creator='support@admin.com'")


class NotificationCreate(NotificationBase):
    creator_id: str
    module: str
    mentions: Optional[list] = None


class NotificationSetting(pydantic.BaseModel):
    organization_id: Optional[str]
    access_level: Optional[str]
    send_via: Optional[SendVia]
    status: Optional[bool] = True


class NotificationSettingUpdate(NotificationSetting):
    access_level: Optional[str]
    send_via: Optional[SendVia]
    status: Optional[bool]
    last_updated: datetime = datetime.now()


class NotificationSettingResponse(NotificationSetting):
    id: str
    date_created: datetime
    last_updated: datetime

    class Config:
        orm_mode = True


class NotificationGroup(pydantic.BaseModel):
    name: str
    members: Optional[List]


class GroupUser(pydantic.BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: str

    class Config:
        orm_mode = True


class GroupMembersOutput(pydantic.BaseModel):
    member_id: str
    date_created: datetime
    user_member: Optional[GroupUser]

    class Config:
        orm_mode = True


class NotificationGroupResponse(NotificationGroup):
    id: str
    date_created: datetime
    last_updated: datetime
    notification_group_members: Optional[List[GroupMembersOutput]]

    class Config:
        orm_mode = True


class NotificationGroupUpdate(NotificationGroup):
    last_updated: datetime = datetime.now()


class NotificationGroupMember(pydantic.BaseModel):
    group_id: str
    member_id: str


class NotificationGroupMemberResponse(NotificationGroupMember):
    id: str
    date_created: datetime
    last_updated: datetime

    class Config:
        orm_mode = True


class NotificationModule(pydantic.BaseModel):
    module_name: str
    status: Optional[bool] = True


class NotificationModuleUpdate(pydantic.BaseModel):
    status: Optional[bool]
    last_updated: datetime = datetime.now()


class NotificationModuleResponse(NotificationModule):
    id: str
    date_created: datetime
    last_updated: datetime

    class Config:
        orm_mode = True


class NotificationGroupModule(pydantic.BaseModel):
    group_id: str
    module_id: str


class NotificationGroupModuleResponse(NotificationGroupModule):
    id: str
    date_created: datetime
    last_updated: datetime

    class Config:
        orm_mode = True


class NotificationUpdate(NotificationBase):
    pass


class NotificationItem(pydantic.BaseModel):
    Notification: Notification
    is_read: bool
    is_cleared: bool

    class Config:
        orm_mode = True


class FetchNotificationsResponse(pydantic.BaseModel):
    page: int
    size: int
    total: int
    items: List[NotificationItem]
    previous_page: Optional[str]
    next_page: Optional[str]

    class Config:
        orm_mode = True
