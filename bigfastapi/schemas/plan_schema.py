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
