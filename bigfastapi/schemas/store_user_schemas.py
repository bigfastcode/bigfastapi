import datetime as dt
from typing import Optional
from .email_schema import Email
from pydantic import BaseModel
from typing import Optional

class _StoreUserBase(BaseModel):
    store_id: Optional[str]
    user_id: Optional[str]
    role: Optional[str]
    is_deleted: Optional[str]
    date_created: Optional[str]

    class Config:
        orm_mode = True

class UserUpdate(_StoreUserBase):
    email: str

class UpdateRoleResponse(BaseModel):
    message: str
    data: dict = dict(store_id="string", user_id="string", role_id="string", is_deleted="string", date_created="string")
