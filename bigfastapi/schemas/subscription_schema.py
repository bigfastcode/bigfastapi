import datetime as _dt
import pydantic
from uuid import UUID
from typing import List, Optional


class _SubBAse(pydantic.BaseModel):
    plan: str
    organization_id: str


class SubcriptionBase(_SubBAse):
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


class CreateSubscription(_SubBAse):
    pass
