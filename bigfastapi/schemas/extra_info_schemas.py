import datetime
import pydantic
from pydantic import Field, BaseModel
from uuid import UUID
from typing import List, Optional


class ExtraInfoBase(BaseModel):
    id: Optional[str]
    key: str
    value: str
    value_dt: Optional[str]
    date_created: Optional[datetime.datetime] = datetime.datetime.now()
    last_updated: Optional[datetime.datetime] = datetime.datetime.now()

    class Config:
        orm_mode = True


class ExtraInfoUpdate(BaseModel):
    key: Optional[str]
    value: Optional[str]
