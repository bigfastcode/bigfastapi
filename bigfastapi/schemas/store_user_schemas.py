import datetime as dt
from typing import Optional
from .email_schema import Email
import pydantic as _pydantic
from typing import Optional

class _StoreUserBase(_pydantic.BaseModel):
    store_id = str
    user_id = str
    role = str
    is_deleted = str
    date_created = str

class StoreUserBase(_pydantic.BaseModel):
    store_id = Optional[str]
    user_id = Optional[str]
    role = Optional[str]
    is_deleted = Optional[str]
    date_created = Optional[str]

class UserUpdate(StoreUserBase):
    email = str
