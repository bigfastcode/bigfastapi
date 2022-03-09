import datetime as dt
from typing import Optional
from .email_schema import Email
import pydantic
from typing import Optional


class StoreUserBase(pydantic.BaseModel):
    store_id = Optional[str]
    user_id = Optional[str]
    role = Optional[str]
    is_deleted = Optional[str]
    date_created = Optional[str]

    class Config:
        arbitrary_types_allowed = True

class UserUpdate(StoreUserBase):
    email: str