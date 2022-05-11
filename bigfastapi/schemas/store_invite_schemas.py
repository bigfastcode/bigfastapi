import datetime as dt
from typing import Optional
from .email_schema import Email
from pydantic import BaseModel

class _InviteBase(BaseModel):
    id: Optional[str]
    user_email: Optional[str]
    user_id: Optional[str]
    user_role: Optional[str]
    is_accepted: Optional[bool] = False
    is_revoked: Optional[bool] = False
    is_deleted: Optional[bool] = False

    class Config:
        orm_mode = True

class UserInvite(_InviteBase):
    store: dict
    app_url: str
    email_details: Email

class Invite(_InviteBase):
    store_id: str
    invite_code: str
    
    class Config:
        orm_mode = True


class StoreUser(_InviteBase):
    organization_id: str
    user_id: str

class InviteResponse(BaseModel):
    message: str

class SingleInviteResponse(BaseModel):
    invite: _InviteBase
    user: str = 'exists'

class AcceptInviteResponse(_InviteBase):
    is_accepted: bool = True
    is_deleted: bool = True

class RevokedInviteResponse(_InviteBase):
    is_revoked: bool = True
    is_deleted: bool = True

class DeclinedInviteResponse(_InviteBase):
    is_deleted: bool = True