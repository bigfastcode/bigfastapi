import datetime as dt
from typing import Optional
from .email_schema import Email
import pydantic as _pydantic

class _StoreUserBase(_pydantic.BaseModel):
    store_id = str
    user_id = str
    role = str
    is_deleted = str
    date_created = str

    class Config:
        orm_mode = True

class UserUpdate(_StoreUserBase):
    store_id: str
    user_id: str
    role: str
