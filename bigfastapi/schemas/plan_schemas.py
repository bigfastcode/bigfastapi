from typing import Any, Dict, List, Union
import pydantic
from datetime import datetime
from enum import Enum
import json


def is_json(myjson: str):
    try:
        json.loads(myjson)
    except ValueError or TypeError as e:
        return False
    else:
        return True


class Period(str, Enum):
    """Provides choices for the roles of a user in a room.
    ADMIN ['admin'] -> The admin role is the only one that can add or remove users from a room.
    MEMBER ['member'] -> The member role cannot add or remove users from a room
    """

    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"

    def __str__(self):
        """returns string representation of enum choice"""
        return self.value


class PriceOffer(pydantic.BaseModel):
    price: float
    duration: int = 1
    period: Period


class PlanDTO(pydantic.BaseModel):
    title: str
    description: str
    price_offers: List[PriceOffer] = None
    available_geographies: List[str] = None
    features: List[str] = None

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, obj: Any) -> "PlanDTO":
        if hasattr(obj, "available_geographies"):
            if type(obj.price_offers) == str:
                setattr(obj, "price_offers", json.loads(obj.price_offers))
                
            if type(obj.available_geographies) is str:
                setattr(
                    obj, "available_geographies", json.loads(obj.available_geographies)
                )

        if hasattr(obj, "features"):
            if type(obj.features) is str:
                setattr(obj, "features", json.loads(obj.features))

        return super().from_orm(obj)


class Plan(PlanDTO):
    id: str
    created_by: str
    date_created: datetime
    last_updated: datetime

    class Config:
        orm_mode = True
