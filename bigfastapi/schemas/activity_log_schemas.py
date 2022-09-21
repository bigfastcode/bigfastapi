import datetime
import pydantic
from pydantic import Field
from uuid import UUID
from typing import List, Optional
from datetime import date as date_type

class ActivitiesLogBase(pydantic.BaseModel):
    action : str = '' 
    object_url : str = ''
    organization_id: str

    class Config:
        orm_mode = True

class DeleteActivitiesLogBase(pydantic.BaseModel):
    organization_id: str

    class Config:
        orm_mode = True


class ActivitiesLogOutput(pydantic.BaseModel):
    id : str
    action : str = ''     
    model_name: str    
    created_at : datetime.datetime

    class Config:
        orm_mode = True

