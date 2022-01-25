from typing import Dict, List, Union
import pydantic
from datetime import datetime
from enum import Enum
import json


def is_json(myjson:str):
  try:
    json.loads(myjson)
  except ValueError as e:
    return False
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
    number: int = 1
    period: Period
    
    

class PlanDTO(pydantic.BaseModel):
    title: str
    description: str
    price_offers: Union[Dict[float, Duration], str] = None
    available_geographies: Union[List[str], str] = None
    features: Union[List[str], str] = None
    
    @pydantic.validator('price_offers')
    def price_offers_to_string(cls, value):
        """converts price_offers from dict to str"""
        if isinstance(value, dict):
            return json.dumps(value)
        return value
    
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
    
    class Config:
        json_encoders = {
            str: lambda value: json.loads(value) if is_json(value) else value
        }

class Plan(PlanDTO):
    id: str
    created_by: str
    date_created: datetime
    last_updated: datetime
    
    class Config:
        orm_mode = True
    