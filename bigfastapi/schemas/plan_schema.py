import datetime as _dt
import pydantic
from uuid import UUID
from typing import List, Optional


class PlanReqBase(pydantic.BaseModel):
    price: float
    access_type: str
    duration: int


class PlanResBase(PlanReqBase):
    id: str


class PlanResponse(PlanResBase):
    date_created: _dt.datetime
    last_updated: _dt.datetime


class ResponseDefault(pydantic.BaseModel):
    status: str
    resource_type: str


class ResponseSingle(ResponseDefault):
    data: PlanResponse


class ResponseList(ResponseDefault):
    data: List[PlanResponse]
