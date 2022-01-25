from tkinter import E
from typing import Any, Dict, List, Union
import pydantic
from datetime import datetime
from enum import Enum
import json


def is_json(myjson:str):
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
    YEARS = 'years'

    def __str__(self):
        """returns string representation of enum choice"""
        return self.value


class Duration(pydantic.BaseModel):
    length: int = 1
    period: Period
    


class PlanDTO(pydantic.BaseModel):
    title: str
    description: str
    price_offers: Dict[float, Duration] = None
    available_geographies: List[str] = None
    features: List[str] = None
    
    @pydantic.validator('available_geographies')
    def available_geo_to_string(cls, value):
        """converts available_geographies from list to str"""
        if isinstance(value, list):
            return json.dumps(value)
        return value
    
    @pydantic.validator('features')
    def features_to_string(cls, value):
        """converts fetures from list to str"""
        if isinstance(value, list):
            return json.dumps(value)
        return value
    
    
    @classmethod
    def from_orm(cls, obj: Any): 
        if hasattr(obj, "available_geographies"):       
            if is_json(obj.available_geographies):
                setattr(obj, "available_geographies", json.loads(obj.available_geographies))
        
        if hasattr(obj, "features"):
            if is_json(obj.features):
                setattr(obj, "features", json.loads(obj.features))
        
        return obj
        

class Plan(PlanDTO):
    id: str
    created_by: str
    date_created: datetime
    last_updated: datetime
    
    class Config:
        orm_mode = True
    