import datetime as dt
from typing import Optional
from .email_schema import Email
import pydantic as _pydantic

class _InviteBase(_pydantic.BaseModel):
    user_email: Optional[str]
    user_id: Optional[str]
    user_role: Optional[str]
    is_accepted: Optional[bool]
    is_revoked: Optional[bool]
    is_deleted: Optional[bool]

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