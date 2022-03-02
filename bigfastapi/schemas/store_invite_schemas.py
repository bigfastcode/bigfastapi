import datetime as dt

from .email_schema import Email
import pydantic as _pydantic

class _InviteBase(_pydantic.BaseModel):
    user_email: str

class UserInvite(_InviteBase):
    store: dict
    user_id: str
    user_role: str
    app_url: str
    email_details: Email

    class Config:
        orm_mode = True


class StoreUser(_InviteBase):
    organization_id: str
    user_id: str