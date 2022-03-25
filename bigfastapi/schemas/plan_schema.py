import datetime as _dt
import pydantic
from uuid import UUID
from typing import List, Optional


class PlanReqBase(pydantic.BaseModel):
    credit_price: int
    access_type: str
    duration: int


class PlanResBase(PlanReqBase):
    id: str


class PlanResponse(PlanResBase):
    date_created: _dt.datetime
    last_updated: _dt.datetime

    class Config:
        orm_mode = True


class PlanResponseDef(pydantic.BaseModel):
    status: str
    resource_type: str


class ResponseSingle(PlanResponseDef):
    data: PlanResponse


class ResponseList(PlanResponseDef):
    data: List[PlanResponse]
