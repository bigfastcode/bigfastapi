import datetime as _dt
import pydantic
from uuid import UUID
from typing import List, Optional


class SubBase(pydantic.BaseModel):
    plan: str
    organization_id: str


class SubcriptionBase(SubBase):
    id: str
    date_created: _dt.datetime

    class Config:
        orm_mode = True


class ResponseDefault(pydantic.BaseModel):
    status: str
    resource_type: str


class ResponseSingle(ResponseDefault):
    data: SubcriptionBase


class ResponseList(ResponseDefault):
    data: List[SubcriptionBase]


class CreateSubscription(SubBase):
    pass
