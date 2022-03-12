import datetime as dt
from typing import Optional
from .email_schema import Email
from pydantic import BaseModel, EmailStr
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
